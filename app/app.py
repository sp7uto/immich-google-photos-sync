import os, sqlite3, threading, time, json, csv, io, tempfile
from pathlib import Path
from flask import Flask, render_template, jsonify, request, Response
import requests

APP_VERSION="3.0"
DATA=Path("/data"); DATA.mkdir(exist_ok=True)
DB=DATA/"state.db"
CFG=DATA/"config.json"
IMMICH_URL=os.getenv("IMMICH_URL","").rstrip("/")
IMMICH_KEY=os.getenv("IMMICH_API_KEY","")
DEFAULT_ALBUM=os.getenv("SOURCE_ALBUM","Do Google Photos")
PORT=int(os.getenv("PORT","8787"))
app=Flask(__name__)

state={"running":False,"paused":False,"cancel":False,"current":"","done":0,"total":0,"logs":[]}
lock=threading.Lock()

def db():
    c=sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS sent(
      asset_id TEXT PRIMARY KEY, checksum TEXT, filename TEXT, sent_at INTEGER,
      google_album TEXT, media_item_id TEXT, status TEXT DEFAULT 'sent', error TEXT)""")
    c.commit(); return c

def cfg():
    base={"source_album":DEFAULT_ALBUM,"google_album":"Immich Uploads","include_video":False,
          "photo_ext":["jpg","jpeg","heic","png","webp"],"post_action":"keep","require_confirm":True}
    if CFG.exists():
        try: base.update(json.loads(CFG.read_text()))
        except: pass
    return base

def save_cfg(x): CFG.write_text(json.dumps(x,ensure_ascii=False,indent=2))

def ih():
    return {"x-api-key":IMMICH_KEY,"Accept":"application/json"}

def albums():
    r=requests.get(f"{IMMICH_URL}/api/albums",headers=ih(),timeout=20); r.raise_for_status()
    return r.json()

def source_assets():
    c=cfg(); name=c["source_album"]
    al=next((a for a in albums() if a.get("albumName")==name),None)
    if not al: return []
    try:
        r=requests.post(f"{IMMICH_URL}/api/search/metadata",headers={**ih(),"Content-Type":"application/json"},
                        json={"albumIds":[al["id"]],"page":1,"size":1000},timeout=30)
        if r.ok:
            j=r.json(); return j.get("assets",{}).get("items",j.get("items",[]))
    except: pass
    r=requests.get(f"{IMMICH_URL}/api/albums/{al['id']}",headers=ih(),timeout=30); r.raise_for_status()
    return r.json().get("assets",[])

def ext_ok(a,c):
    typ=(a.get("type") or "").lower()
    if typ=="video": return c["include_video"]
    name=a.get("originalFileName","")
    ext=name.rsplit(".",1)[-1].lower() if "." in name else ""
    return ext in c["photo_ext"]

def sent_ids():
    c=db(); rows={r[0] for r in c.execute("select asset_id from sent where status='sent'")}; c.close(); return rows

def log(s):
    with lock:
        state["logs"].append(time.strftime("%H:%M:%S")+"  "+s)
        state["logs"]=state["logs"][-300:]

def google_ready():
    return (DATA/"credentials.json").exists() and (DATA/"token.json").exists()

def google_upload(asset, album):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    cred=Credentials.from_authorized_user_file(str(DATA/"token.json"))
    if cred.expired and cred.refresh_token:
        cred.refresh(Request()); (DATA/"token.json").write_text(cred.to_json())
    h={"Authorization":f"Bearer {cred.token}","Content-Type":"application/octet-stream",
       "X-Goog-Upload-Protocol":"raw","X-Goog-Upload-File-Name":asset.get("originalFileName","photo")}
    # Stage the source on disk after 8 MiB, avoiding unbounded RAM usage.
    # A seekable file lets requests supply Content-Length to Google Photos.
    with requests.get(f"{IMMICH_URL}/api/assets/{asset['id']}/original",headers=ih(),stream=True,timeout=120) as raw:
        raw.raise_for_status()
        with tempfile.SpooledTemporaryFile(max_size=8*1024*1024,mode="w+b",dir=DATA) as upload_file:
            for chunk in raw.iter_content(chunk_size=1024*1024):
                if chunk:
                    upload_file.write(chunk)
            if upload_file.tell()==0:
                raise RuntimeError("Immich returned an empty asset")
            upload_file.seek(0)
            up=requests.post("https://photoslibrary.googleapis.com/v1/uploads",headers=h,data=upload_file,timeout=180)
            up.raise_for_status()
    token=up.text.strip()
    if not token:
        raise RuntimeError("Google Photos returned an empty upload token")
    body={"newMediaItems":[{"description":"Uploaded from Immich","simpleMediaItem":{"uploadToken":token}}]}
    cr=requests.post("https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate",
                     headers={"Authorization":f"Bearer {cred.token}","Content-Type":"application/json"},
                     json=body,timeout=60); cr.raise_for_status()
    results=cr.json().get("newMediaItemResults",[])
    if len(results)!=1:
        raise RuntimeError("Google Photos returned an unexpected number of media results")
    res=results[0]
    if res.get("status",{}).get("code",0) not in (0,None):
        raise RuntimeError(str(res["status"]))
    media_id=res.get("mediaItem",{}).get("id")
    if not media_id:
        raise RuntimeError("Google Photos did not return a media item ID")
    return media_id

def worker(ids):
    try:
        _run_worker(ids)
    except Exception as exc:
        log("BŁĄD kolejki: "+str(exc))
    finally:
        with lock:
            state["running"]=False
            state["current"]=""

def _run_worker(ids):
    c=cfg(); aset={a["id"]:a for a in source_assets()}
    already_sent=sent_ids()
    queue=[aset[i] for i in dict.fromkeys(ids) if i in aset and ext_ok(aset[i],c) and i not in already_sent]
    with lock: state.update(total=len(queue))
    log(f"Start: {len(queue)} plików")
    con=db()
    try:
        for a in queue:
            while state["paused"] and not state["cancel"]: time.sleep(.4)
            if state["cancel"]: log("Anulowano przed następnym plikiem."); break
            with lock: state["current"]=a.get("originalFileName",a["id"])
            try:
                mid=google_upload(a,c["google_album"])
                con.execute("INSERT OR REPLACE INTO sent(asset_id,filename,sent_at,google_album,media_item_id,status,error) VALUES(?,?,?,?,?,'sent','')",
                            (a["id"],a.get("originalFileName",""),int(time.time()),c["google_album"],mid)); con.commit()
                log("OK  "+a.get("originalFileName",""))
            except Exception as e:
                con.execute("INSERT OR REPLACE INTO sent(asset_id,filename,sent_at,google_album,status,error) VALUES(?,?,?,?, 'error',?)",
                            (a["id"],a.get("originalFileName",""),int(time.time()),c["google_album"],str(e))); con.commit()
                log("BŁĄD  "+a.get("originalFileName","")+": "+str(e))
            with lock: state["done"]+=1
    finally:
        con.close()
    log("Koniec kolejki.")

@app.get("/")
def home(): return render_template("index.html",version=APP_VERSION)

@app.get("/api/preview")
def preview():
    c=cfg(); ss=sent_ids()
    try: aa=[a for a in source_assets() if ext_ok(a,c)]
    except Exception as e: return jsonify({"error":str(e)}),500
    items=[{"id":a["id"],"name":a.get("originalFileName",""),"sent":a["id"] in ss,
            "type":a.get("type",""),"size":a.get("exifInfo",{}).get("fileSizeInByte")} for a in aa]
    return jsonify({"items":items,"total":len(items),"new":sum(not x["sent"] for x in items),
                    "sent":sum(x["sent"] for x in items),"config":c})

@app.get("/thumb/<aid>")
def thumb(aid):
    r=requests.get(f"{IMMICH_URL}/api/assets/{aid}/thumbnail",headers=ih(),params={"size":"preview"},timeout=30)
    return Response(r.content,status=r.status_code,content_type=r.headers.get("content-type","image/jpeg"))

@app.post("/api/send")
def send():
    payload=request.get_json(silent=True) or {}
    ids=payload.get("ids",[])
    if not isinstance(ids,list) or not ids or not all(isinstance(i,str) and i.strip() for i in ids):
        return jsonify({"error":"Nieprawidłowa lista identyfikatorów"}),400
    with lock:
        if state["running"]: return jsonify({"error":"Synchronizacja już trwa"}),409
        state.update(running=True,paused=False,cancel=False,done=0,total=0,current="")
    try:
        threading.Thread(target=worker,args=(ids,),daemon=True).start()
    except Exception:
        with lock:
            state["running"]=False
        app.logger.exception("Unable to start transfer worker")
        return jsonify({"error":"Nie udało się uruchomić kolejki"}),500
    return jsonify({"ok":True})

@app.post("/api/control/<cmd>")
def control(cmd):
    if cmd not in ("pause","resume","cancel"):
        return jsonify({"error":"Unknown control command"}),400
    with lock:
        if cmd=="pause": state["paused"]=True
        elif cmd=="resume": state["paused"]=False
        else:
            state["cancel"]=True
            state["paused"]=False
    return jsonify({"ok":True})

@app.get("/api/status")
def status():
    with lock:
        snapshot={**state,"logs":list(state["logs"])}
    return jsonify(snapshot)

@app.route("/api/config",methods=["GET","POST"])
def config():
    if request.method=="GET": return jsonify(cfg())
    x=cfg(); x.update(request.json or {}); save_cfg(x); return jsonify(x)

@app.get("/api/history.csv")
def history_csv():
    con=db(); rows=con.execute("select filename,sent_at,google_album,status,error from sent order by sent_at desc").fetchall(); con.close()
    s=io.StringIO(); w=csv.writer(s); w.writerow(["filename","sent_at","google_album","status","error"]); w.writerows(rows)
    return Response(s.getvalue(),mimetype="text/csv",headers={"Content-Disposition":"attachment; filename=immich-google-history.csv"})

@app.get("/api/backup")
def backup():
    out=DATA/"state-backup.db"; src=db(); dst=sqlite3.connect(out); src.backup(dst); dst.close(); src.close()
    return jsonify({"ok":True,"path":"/data/state-backup.db"})

@app.get("/api/test")
def test():
    try:
        a=albums()
        return jsonify({"immich":True,"albums":len(a),"google":google_ready(),"version":APP_VERSION})
    except Exception as e: return jsonify({"immich":False,"google":google_ready(),"error":str(e),"version":APP_VERSION})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=PORT,threaded=True)
