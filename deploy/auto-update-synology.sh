#!/bin/sh
# Intended for DSM Task Scheduler, run as root every 30 minutes.
# Only deploy a version named in main/VERSION and published to GHCR.
set -eu
BASE=/volume1/docker/immich-google-sync
NAME=immich-google-sync
REPO=ghcr.io/sp7uto/immich-google-photos-sync
URL=https://raw.githubusercontent.com/sp7uto/immich-google-photos-sync/main/VERSION
[ "$(id -u)" -eq 0 ] || { echo "Run as root"; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "curl unavailable"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "docker unavailable"; exit 1; }
[ -f "$BASE/deploy/update-synology.sh" ] || { echo "Updater missing"; exit 1; }
[ -d "$BASE/data" ] || { echo "Production data missing"; exit 1; }
# If a deployment is underway, leave it alone.
[ ! -d "$BASE/.update-lock" ] || { echo "Deployment in progress; skip"; exit 0; }
VERSION=$(curl -fsSL --connect-timeout 5 --max-time 15 "$URL" | tr -d '\r\n')
case "$VERSION" in
  v[0-9]*.[0-9]*.[0-9]*) ;;
  *) echo "Invalid upstream version"; exit 1 ;;
esac
# Reject extra characters, untrusted tags or malformed version strings.
echo "$VERSION" | grep -Eq '^v[0-9]+\.[0-9]+\.[0-9]+$' || { echo "Invalid version format"; exit 1; }
CURRENT=$(docker inspect -f '{{.Config.Image}}' "$NAME" 2>/dev/null) || { echo "Production container missing"; exit 1; }
TARGET="$REPO:$VERSION"
if [ "$CURRENT" = "$TARGET" ]; then
  echo "Up to date: $VERSION"
  exit 0
fi
echo "Published version candidate: $VERSION; running image: $CURRENT"
# Existing updater performs pull, SQLite snapshot, health check and rollback.
sh "$BASE/deploy/update-synology.sh" "$VERSION"
