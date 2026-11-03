#!/bin/sh
# Synology updater for the existing, manually deployed container.
# Explicit execution only. Never schedules itself.
set -u
NAME=immich-google-sync
BASE=/volume1/docker/immich-google-sync
IMAGE_REPO=ghcr.io/sp7uto/immich-google-photos-sync
VERSION=${1:-}
case "$VERSION" in
  v[0-9]*.[0-9]*.[0-9]*) ;;
  *) echo "Usage: sudo sh update-synology.sh vX.Y.Z"; exit 2 ;;
esac
command -v docker >/dev/null 2>&1 || { echo "Docker unavailable"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Python3 unavailable"; exit 1; }
[ "$(id -u)" = 0 ] || { echo "Run as root via sudo"; exit 1; }
[ -d "$BASE/data" ] || { echo "Missing production data"; exit 1; }
[ -f "$BASE/data/state.db" ] || { echo "Missing state.db"; exit 1; }
docker inspect "$NAME" >/dev/null 2>&1 || { echo "Production container missing"; exit 1; }
[ "$(docker inspect -f '{{.State.Running}}' "$NAME")" = true ] || { echo "Production is not running"; exit 1; }
# Avoid interfering with manual or concurrent deployments.
LOCK="$BASE/.update-lock"
if ! mkdir "$LOCK" 2>/dev/null; then echo "Update already running (or stale lock at $LOCK)"; exit 1; fi
trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT HUP INT TERM
STAMP=$(date +%Y%m%d-%H%M%S)
SAVE="$BASE/update-backups/$STAMP"
mkdir -p "$SAVE" || exit 1
chmod 700 "$SAVE"
OLD="$NAME-before-update-$STAMP"
TARGET="$IMAGE_REPO:$VERSION"
echo "Preparing $TARGET"
docker inspect "$NAME" > "$SAVE/container.json" || exit 1
docker inspect -f '{{.Image}}' "$NAME" > "$SAVE/old-image-id" || exit 1
# Secrets remain local, protected, and are never printed.
docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' "$NAME" > "$SAVE/container.env" || exit 1
chmod 600 "$SAVE/container.env"
# Preserve current album/token/config in case they change later.
cp -p "$BASE/data/config.json" "$SAVE/config.json" 2>/dev/null || true
cp -p "$BASE/data/token.json" "$SAVE/token.json" 2>/dev/null || true
python3 - "$BASE/data/state.db" "$SAVE/state.db" <<'PY'
import sqlite3, sys
with sqlite3.connect(sys.argv[1]) as src, sqlite3.connect(sys.argv[2]) as dst:
    src.backup(dst)
print("SQLite snapshot: OK")
PY
[ "$?" = 0 ] || { echo "Backup failed; production untouched"; exit 1; }
chmod 600 "$SAVE/state.db"
docker pull "$TARGET" || { echo "Pull failed; production untouched"; exit 1; }
# Deployment contract: single host port 8787, existing bridge network and bind mount.
NETWORK=$(docker inspect -f '{{range $name, $value := .NetworkSettings.Networks}}{{$name}}{{println}}{{end}}' "$NAME" | head -n 1)
[ -n "$NETWORK" ] || { echo "Cannot identify Docker network"; exit 1; }
[ "$(docker inspect -f '{{range .Mounts}}{{if eq .Destination "/data"}}{{.Source}}{{end}}{{end}}' "$NAME")" = "$BASE/data" ] || {
  echo "Unexpected production /data mount; aborting"; exit 1;
}
PORT=$(docker inspect -f '{{(index (index .HostConfig.PortBindings "8787/tcp") 0).HostPort}}' "$NAME" 2>/dev/null)
[ "$PORT" = 8787 ] || { echo "Unexpected production port; aborting"; exit 1; }
RESTART=$(docker inspect -f '{{.HostConfig.RestartPolicy.Name}}' "$NAME")
[ "$RESTART" = unless-stopped ] || { echo "Unexpected restart policy; aborting"; exit 1; }
echo "Stopping production briefly; old container retained as $OLD"
docker stop "$NAME" || exit 1
if ! docker rename "$NAME" "$OLD"; then
  docker start "$NAME" || true
  exit 1
fi
if docker run -d --name "$NAME" --restart unless-stopped \
    --network "$NETWORK" --env-file "$SAVE/container.env" \
    -p 8787:8787 -v "$BASE/data:/data" "$TARGET"; then
  sleep 3
  if docker exec "$NAME" python3 -c 'import os,urllib.request,base64; r=urllib.request.Request("http://127.0.0.1:8787/api/status"); p=os.getenv("PANEL_PASSWORD"); r.add_header("Authorization","Basic "+base64.b64encode(("health:"+p).encode()).decode()) if p else None; assert urllib.request.urlopen(r,timeout=10).status==200' >/dev/null 2>&1; then
    echo "SUCCESS: $VERSION is running. Previous container: $OLD"
    echo "Backup: $SAVE"
    exit 0
  fi
fi
echo "Health check failed; restoring previous container"
docker rm -f "$NAME" >/dev/null 2>&1 || true
if docker rename "$OLD" "$NAME" && docker start "$NAME"; then
  echo "ROLLBACK OK: old production restored; data not overwritten."
else
  echo "CRITICAL: automatic rollback failed; old container is $OLD"
fi
exit 1
