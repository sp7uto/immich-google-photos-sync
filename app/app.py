import os, sqlite3, threading, time, json, csv, io, tempfile, hmac
from urllib.parse import urlsplit
from pathlib import Path
from flask import Flask, render_template, jsonify, request, Response
import requests

APP_VERSION="3.1-dev"
DATA=Path("/data"); DATA.mkdir(exist_ok=True)
DB=DATA/"state.db"
CFG=DATA/"config.json"
IMMICH_URL=os.getenv("IMMICH_URL","").rstrip("/")
IMMICH_KEY=os.getenv("IMMICH_API_KEY","")
DEFAULT_ALBUM=os.getenv("SOURCE_ALBUM","do publikacji")
PORT=int(os.getenv("PORT","8787"))
app=Flask(__name__)

# Optional HTTP Basic authentication. Configure PANEL_PASSWORD for remote access.
PANEL_PASSWORD=os.getenv("PANEL_PASSWORD","")
AUTH_MAX_FAILURES=5
AUTH_WINDOW_SECONDS=60
AUTH_LOCK_SECONDS=60
_auth_failures=[]
_auth_locked_until=0.0
_auth_lock=threading.Lock()

@app.before_request
def require_panel_auth():
    global _auth_locked_until
    if not PANEL_PASSWORD:
        return None
    now=time.monotonic()
    with _auth_lock:
        if now<_auth_locked_until:
            return Response("Too many authentication attempts",429,{"Retry-After":str(AUTH_LOCK_SECONDS)})
        _auth_failures[:]=[t for t in _auth_failures if now-t<AUTH_WINDOW_SECONDS]
        auth=request.authorization
        valid=(auth is not None and (auth.type or "").lower()=="basic" and
               hmac.compare_digest(auth.password or "",PANEL_PASSWORD))
        if valid:
            _auth_failures.clear()
            return None
        _auth_failures.append(now)
        if len(_auth_failures)>=AUTH_MAX_FAILURES:
            _auth_locked_until=now+AUTH_LOCK_SECONDS
            _auth_failures.clear()
            return Response("Too many authentication attempts",429,{"Retry-After":str(AUTH_LOCK_SECONDS)})
    return Response("Authentication required",401,{"WWW-Authenticate":'Basic realm="Immich Google Sync", charset="UTF-8"'})

@app.before_request
def reject_cross_origin_writes():
    if request.method not in ("POST","PUT","PATCH","DELETE"):
        return None
    if request.headers.get("Sec-Fetch-Site","").lower()=="cross-site":
        return jsonify({"error":"Cross-site request blocked"}),403
    origin=request.headers.get("Origin")
    if origin:
        try:
            source=urlsplit(origin)
            if source.scheme not in ("http","https") or source.netloc.lower()!=request.host.lower():
                return jsonify({"error":"Cross-origin request blocked"}),403
        except ValueError:
            return jsonify({"error":"Invalid Origin header"}),403
    return None

@app.after_request
def security_headers(response):
    # The panel exposes private thumbnails, filenames, history and transfer controls.
    response.headers["Cache-Control"]="no-store"
    response.headers["X-Content-Type-Options"]="nosniff"
    response.headers["X-Frame-Options"]="DENY"
    response.headers["Referrer-Policy"]="no-referrer"
    return response

state={"running":False,"paused":False,"cancel":False,"current":"","done":0,"total":0,"logs":[]}
lock=threading.Lock()

def db():
    c=sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS sent(
      asset_id TEXT PRIMARY KEY, checksum TEXT, filename TEXT, sent_at INTEGER,
      google_album TEXT, media_item_id TEXT, status TEXT DEFAULT 'sent', error TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS review_audit(
      id INTEGER PRIMARY KEY AUTOINCREMENT, asset_id TEXT NOT NULL,
      reviewed_at INTEGER NOT NULL, previous_status TEXT NOT NULL,
      decision TEXT NOT NULL, media_item_id TEXT)""")
    c.commit(); return c

def cfg():
    base={"source_album":DEFAULT_ALBUM,"google_album":"do publikacji","google_album_id":"","include_video":False,
          "photo_ext":["jpg","jpeg","heic","png","webp"],"post_action":"keep","require_confirm":True}
    if CFG.exists():
        try: base.update(json.loads(CFG.read_text()))
        except: pass
    return base

def save_cfg(x):
    fd, temporary=tempfile.mkstemp(prefix=".config-",suffix=".tmp",dir=DATA)
    try:
        os.fchmod(fd,0o600)
        with os.fdopen(fd,"w",encoding="utf-8") as output:
            json.dump(x,output,ensure_ascii=False,indent=2)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary,CFG)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

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
        page=1
        found=[]
        seen=set()
        while True:
            r=requests.post(f"{IMMICH_URL}/api/search/metadata",headers={**ih(),"Content-Type":"application/json"},
                            json={"albumIds":[al["id"]],"page":page,"size":1000},timeout=30)
            if not r.ok:
                if page==1:
                    break  # Older Immich versions may require the album-detail endpoint.
                r.raise_for_status()  # Never silently return a partial album.
            j=r.json()
            section=j.get("assets",j)
            items=section.get("items")
            if not isinstance(items,list):
                raise RuntimeError("Unexpected Immich search response; cannot verify complete album")
            ids=[a.get("id") for a in items]
            if any(not isinstance(i,str) or not i for i in ids) or len(ids)!=len(set(ids)) or seen.intersection(ids):
                raise RuntimeError("Repeated or invalid Immich search results; refusing incomplete preview")
            seen.update(ids)
            found.extend(items)
            next_page=section.get("nextPage")
            if next_page is not None:
                if not str(next_page).isdigit() or int(next_page)<=page:
                    raise RuntimeError("Invalid Immich pagination cursor")
                page=int(next_page)
            elif len(items)==1000:
                page+=1  # Also support Immich responses without nextPage.
            else:
                return found
    except requests.RequestException:
        if page!=1:
            raise
    r=requests.get(f"{IMMICH_URL}/api/albums/{al['id']}",headers=ih(),timeout=30); r.raise_for_status()
    return r.json().get("assets",[])

def ext_ok(a,c):
    typ=(a.get("type") or "").lower()
    if typ=="video": return c["include_video"]
    name=a.get("originalFileName","")
    ext=name.rsplit(".",1)[-1].lower() if "." in name else ""
    return ext in c["photo_ext"]

def sent_ids():
    c=db(); rows={r[0] for r in c.execute("select asset_id from sent where status in ('sent','uploading','needs_review')")}; c.close(); return rows

def transfer_statuses():
    con=db()
    try:
        return dict(con.execute("select asset_id,status from sent"))
    finally:
        con.close()

def log(s):
    with lock:
        state["logs"].append(time.strftime("%H:%M:%S")+"  "+s)
        state["logs"]=state["logs"][-300:]

def save_token_atomic(credentials):
    target=DATA/"token.json"
    fd, temporary=tempfile.mkstemp(prefix=".token-",suffix=".tmp",dir=DATA)
    try:
        os.fchmod(fd,0o600)
        with os.fdopen(fd,"w",encoding="utf-8") as output:
            output.write(credentials.to_json())
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary,target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

def google_ready():
    return (DATA/"credentials.json").exists() and (DATA/"token.json").exists()

def google_credentials():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    cred=Credentials.from_authorized_user_file(str(DATA/"token.json"))
    if cred.expired and cred.refresh_token:
        cred.refresh(Request()); save_token_atomic(cred)
    if not cred.valid or not cred.token:
        raise RuntimeError("Google Photos OAuth token is not valid")
    return cred

@app.post("/api/google-album/create")
def create_google_album():
    if request.headers.get("X-Requested-With")!="XMLHttpRequest":
        return jsonify({"error":"Missing panel request header"}),403
    payload=request.get_json(silent=True)
    if not isinstance(payload,dict):
        return jsonify({"error":"Invalid request"}),400
    with lock:
        if state["running"]:
            return jsonify({"error":"Cannot create an album while transferring"}),409
        settings=cfg()
        name=settings["google_album"]
        if settings.get("google_album_id"):
            return jsonify({"error":"Destination album already configured"}),409
        if payload.get("confirmation")!=f"CREATE:{name}":
            return jsonify({"error":"Explicit album creation confirmation required"}),400
        try:
            cred=google_credentials()
            response=requests.post("https://photoslibrary.googleapis.com/v1/albums",
                                   headers={"Authorization":f"Bearer {cred.token}","Content-Type":"application/json"},
                                   json={"album":{"title":name}},timeout=60)
            response.raise_for_status()
            album_id=response.json().get("id")
            if not isinstance(album_id,str) or not album_id:
                raise RuntimeError("Google Photos created album without returning an ID; check Google Photos before retrying")
            settings["google_album_id"]=album_id
            save_cfg(settings)
        except Exception:
            app.logger.exception("Google album creation failed; inspect Google Photos before retrying")
            return jsonify({"error":"Album creation was not confirmed locally. Check Google Photos before trying again."}),502
    return jsonify({"ok":True,"album_id":album_id,"name":name})

def google_upload(asset, album, album_id):
    if not album_id:
        raise RuntimeError("Google destination album is not configured")
    cred=google_credentials()
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
    body={"albumId":album_id,"newMediaItems":[{"description":"Uploaded from Immich","simpleMediaItem":{"uploadToken":token}}]}
    cr=requests.post("https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate",
                     headers={"Authorization":f"Bearer {cred.token}","Content-Type":"application/json"},
                     json=body,timeout=60)
    if not cr.ok:
        # Do not log OAuth headers or upload tokens; response body is diagnostic only.
        detail=cr.text[:1200].replace("\\n"," ")
        raise RuntimeError(f"Google Photos batchCreate HTTP {cr.status_code}: {detail}")
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
    c=cfg()
    album_id=c.get("google_album_id")
    if not album_id:
        raise RuntimeError("Configure the destination Google Photos album before sending")
    aset={a["id"]:a for a in source_assets()}
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
                # Persist before contacting Google: interrupted uploads require manual review.
                con.execute("INSERT OR REPLACE INTO sent(asset_id,filename,sent_at,google_album,status,error) VALUES(?,?,?,?,'uploading','')",
                            (a["id"],a.get("originalFileName",""),int(time.time()),c["google_album"])); con.commit()
                mid=google_upload(a,c["google_album"],album_id)
                con.execute("INSERT OR REPLACE INTO sent(asset_id,filename,sent_at,google_album,media_item_id,status,error) VALUES(?,?,?,?,?,'sent','')",
                            (a["id"],a.get("originalFileName",""),int(time.time()),c["google_album"],mid)); con.commit()
                log("OK  "+a.get("originalFileName",""))
            except Exception as e:
                con.execute("UPDATE sent SET status='needs_review', error=? WHERE asset_id=?",
                            (str(e),a["id"])); con.commit()
                log("BŁĄD  "+a.get("originalFileName","")+": "+str(e))
            with lock: state["done"]+=1
    finally:
        con.close()
    log("Koniec kolejki.")

@app.get("/")
def home(): return render_template("index.html",version=APP_VERSION)

@app.get("/api/preview")
def preview():
    c=cfg(); statuses=transfer_statuses()
    try: aa=[a for a in source_assets() if ext_ok(a,c)]
    except Exception as e: return jsonify({"error":str(e)}),500
    items=[{"id":a["id"],"name":a.get("originalFileName",""),"sent":statuses.get(a["id"])=="sent","review":statuses.get(a["id"]) in ("uploading","needs_review"),
            "type":a.get("type",""),"size":a.get("exifInfo",{}).get("fileSizeInByte")} for a in aa]
    return jsonify({"items":items,"total":len(items),"new":sum(not x["sent"] and not x["review"] for x in items),
                    "sent":sum(x["sent"] for x in items),"review":sum(x["review"] for x in items),"config":c})

@app.get("/thumb/<aid>")
def thumb(aid):
    r=requests.get(f"{IMMICH_URL}/api/assets/{aid}/thumbnail",headers=ih(),params={"size":"preview"},timeout=30)
    return Response(r.content,status=r.status_code,content_type=r.headers.get("content-type","image/jpeg"))

@app.post("/api/send")
def send():
    if request.headers.get("X-Requested-With")!="XMLHttpRequest":
        return jsonify({"error":"Missing panel request header"}),403
    payload=request.get_json(silent=True) or {}
    ids=payload.get("ids",[])
    if not isinstance(ids,list) or not ids or not all(isinstance(i,str) and i.strip() for i in ids):
        return jsonify({"error":"Nieprawidłowa lista identyfikatorów"}),400
    if not cfg().get("google_album_id"):
        return jsonify({"error":"Najpierw skonfiguruj album docelowy Google Photos"}),409
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
    # Custom request header cannot be submitted by a cross-site HTML form.
    if request.headers.get("X-Requested-With")!="XMLHttpRequest":
        return jsonify({"error":"Missing panel request header"}),403
    if cmd not in ("pause","resume","cancel"):
        return jsonify({"error":"Unknown control command"}),400
    with lock:
        if cmd=="pause": state["paused"]=True
        elif cmd=="resume": state["paused"]=False
        else:
            state["cancel"]=True
            state["paused"]=False
    return jsonify({"ok":True})

@app.post("/api/session/clear")
def clear_session():
    if request.headers.get("X-Requested-With")!="XMLHttpRequest":
        return jsonify({"error":"Missing panel request header"}),403
    with lock:
        if state["running"]:
            return jsonify({"error":"Cannot clear an active session"}),409
        state.update(paused=False,cancel=False,current="",done=0,total=0,logs=[])
    return jsonify({"ok":True})


@app.get("/api/status")
def status():
    with lock:
        snapshot={**state,"logs":list(state["logs"])}
    return jsonify(snapshot)

@app.route("/api/config",methods=["GET","POST"])
def config():
    if request.method=="GET": return jsonify(cfg())
    changes=request.get_json(silent=True)
    if not isinstance(changes,dict):
        return jsonify({"error":"Configuration must be a JSON object"}),400
    allowed={"source_album","google_album","include_video","photo_ext","post_action","require_confirm"}
    if set(changes)-allowed:
        return jsonify({"error":"Unknown configuration fields"}),400
    for key,value in changes.items():
        if key in ("source_album","google_album") and (not isinstance(value,str) or not value.strip() or len(value)>255):
            return jsonify({"error":"Invalid album name"}),400
        if key in ("include_video","require_confirm") and not isinstance(value,bool):
            return jsonify({"error":"Invalid boolean setting"}),400
        if key=="photo_ext" and (not isinstance(value,list) or not value or len(value)>32 or
                                  any(not isinstance(ext,str) or not ext or len(ext)>16 or
                                      not ext.isascii() or not ext.isalnum() for ext in value)):
            return jsonify({"error":"Invalid photo extensions"}),400
        if key=="post_action" and value!="keep":
            return jsonify({"error":"Unsupported post action"}),400
    x=cfg()
    if x.get("google_album_id") and "google_album" in changes and changes["google_album"]!=x["google_album"]:
        return jsonify({"error":"Cannot rename a configured destination album; existing album ID remains bound"}),409
    x.update(changes); save_cfg(x); return jsonify(x)

@app.post("/api/review/resolve")
def resolve_review():
    if request.headers.get("X-Requested-With")!="XMLHttpRequest":
        return jsonify({"error":"Missing panel request header"}),403
    payload=request.get_json(silent=True)
    if not isinstance(payload,dict):
        return jsonify({"error":"Invalid request"}),400
    aid=payload.get("asset_id")
    decision=payload.get("decision")
    confirmation=payload.get("confirmation")
    media_id=payload.get("media_item_id")
    if not isinstance(aid,str) or not aid.strip() or len(aid)>255:
        return jsonify({"error":"Invalid asset ID"}),400
    if decision not in ("confirmed_sent","retry") or confirmation!=f"{decision}:{aid}":
        return jsonify({"error":"Explicit confirmation required"}),400
    if decision=="confirmed_sent" and (not isinstance(media_id,str) or not media_id.strip() or len(media_id)>255):
        return jsonify({"error":"Google media item ID required"}),400
    with lock:
        if state["running"]:
            return jsonify({"error":"Cannot resolve while a queue is running"}),409
        con=db()
        try:
            row=con.execute("select status from sent where asset_id=?",(aid,)).fetchone()
            if not row or row[0] not in ("uploading","needs_review"):
                return jsonify({"error":"Asset is not pending review"}),409
            if decision=="confirmed_sent":
                con.execute("UPDATE sent SET status='sent',media_item_id=?,error='' WHERE asset_id=?",
                            (media_id.strip(),aid))
            else:
                # Keep the row as an audit trail; 'error' remains retryable by the queue.
                con.execute("UPDATE sent SET status='error',error=? WHERE asset_id=?",
                            ("Manually cleared for retry after external verification",aid))
            con.execute("INSERT INTO review_audit(asset_id,reviewed_at,previous_status,decision,media_item_id) VALUES(?,?,?,?,?)",
                        (aid,int(time.time()),row[0],decision,media_id.strip() if decision=="confirmed_sent" else None))
            con.commit()
        finally:
            con.close()
    log(f"Manual review: {aid} -> {decision}")
    return jsonify({"ok":True,"decision":decision})

@app.get("/api/review-audit.csv")
def review_audit_csv():
    con=db()
    try:
        rows=con.execute("select asset_id,reviewed_at,previous_status,decision,media_item_id from review_audit order by id desc").fetchall()
    finally:
        con.close()
    output=io.StringIO()
    writer=csv.writer(output)
    writer.writerow(["asset_id","reviewed_at","previous_status","decision","media_item_id"])
    writer.writerows(rows)
    return Response(output.getvalue(),mimetype="text/csv",headers={"Content-Disposition":"attachment; filename=immich-google-review-audit.csv"})

@app.get("/api/review.csv")
def review_csv():
    con=db()
    try:
        rows=con.execute("select asset_id,filename,sent_at,google_album,status,error from sent where status in ('uploading','needs_review') order by sent_at desc").fetchall()
    finally:
        con.close()
    output=io.StringIO()
    writer=csv.writer(output)
    writer.writerow(["asset_id","filename","sent_at","google_album","status","error"])
    writer.writerows(rows)
    return Response(output.getvalue(),mimetype="text/csv",headers={"Content-Disposition":"attachment; filename=immich-google-review.csv"})

@app.get("/api/history.csv")
def history_csv():
    con=db(); rows=con.execute("select filename,sent_at,google_album,status,error from sent order by sent_at desc").fetchall(); con.close()
    s=io.StringIO(); w=csv.writer(s); w.writerow(["filename","sent_at","google_album","status","error"]); w.writerows(rows)
    return Response(s.getvalue(),mimetype="text/csv",headers={"Content-Disposition":"attachment; filename=immich-google-history.csv"})

@app.post("/api/backup")
def backup():
    if request.headers.get("X-Requested-With")!="XMLHttpRequest":
        return jsonify({"error":"Missing panel request header"}),403
    out=DATA/"state-backup.db"
    fd, temporary=tempfile.mkstemp(prefix=".state-backup-",suffix=".db",dir=DATA)
    os.close(fd)
    try:
        os.chmod(temporary,0o600)
        src=db()
        try:
            dst=sqlite3.connect(temporary)
            try:
                src.backup(dst)
            finally:
                dst.close()
        finally:
            src.close()
        os.replace(temporary,out)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return jsonify({"ok":True,"path":"/data/state-backup.db"})

@app.get("/api/test")
def test():
    try:
        a=albums()
        return jsonify({"immich":True,"albums":len(a),"google":google_ready(),"version":APP_VERSION})
    except Exception as e: return jsonify({"immich":False,"google":google_ready(),"error":str(e),"version":APP_VERSION})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=PORT,threaded=True)
