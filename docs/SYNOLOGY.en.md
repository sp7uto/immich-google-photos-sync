# Immich → Google Photos Sync — Synology operations

[🇬🇧 English](SYNOLOGY.en.md) · [🇵🇱 Polski](SYNOLOGY-PL.md) · [Home](../README.md)

## Transfer model

This is **not automatic synchronization**. The user manually selects photos from the configured Immich album (default `do publikacji`) and approves uploading them to the **Google Photos library**, without automatic album assignment. Originals remain on Immich.

Requirements: Docker, Immich API connectivity, an API key with `album.read`, `asset.read`, `asset.view` and **`asset.download`** permissions, and Google OAuth scope `photoslibrary.appendonly`.

## Reference Synology DS1525+ deployment (November 2026)

The reference documentation describes a production container `immich-google-sync` using host port `8787` and `/volume1/docker/immich-google-sync/data`, alongside a separate stopped test container `immich-google-sync-test` using port `8788`. These are **installation-specific examples**, not generic default addresses. Do not transfer test SQLite databases into production or expose the private IP addresses and authentication credentials publicly.

## Transfer statuses and duplicates

- `sent`: Google returned a media item ID; do not upload again.
- `uploading` / `needs_review`: uncertain result; verify in Google Photos before retry.
- `error`: retryable only after a conscious decision.
- **Clear session view** clears only in-memory counters and last-session logs, never SQLite.
- An Immich download HTTP 403 may mean the key lacks `asset.download`.
- A Google album-read `403 ACCESS_TOKEN_SCOPE_INSUFFICIENT` is not itself proof that uploading fails: `appendonly` does not grant album reading.
- After an uncertain `mediaItems:batchCreate` error, do not retry blindly; the media might already exist.

## Releases and upgrades

A tagged GitHub release does **not** automatically update Synology. The release workflow may publish a versioned `ghcr.io/sp7uto/immich-google-photos-sync:vX.Y.Z` image. The administrator triggers a controlled deployment. The update script checks the existing container, prevents parallel updates, retains local tokens and configuration, creates a SQLite snapshot, pulls the requested tagged image, and checks `/api/status`. On failure it attempts to restore the previous container.

Run **on the Synology host** after replacing the version placeholder with an actual published version:

```sh
sudo sh /volume1/docker/immich-google-sync/deploy/update-synology.sh vX.Y.Z
```

The reference deployment expects an existing `/volume1/docker/immich-google-sync/data`, port 8787, and restart policy `unless-stopped`. The old container is preserved as `immich-google-sync-before-update-<timestamp>`. Passing an HTTP health check does not prove subsequent Google transfers will succeed.

## Optional periodic update check

The `deploy/auto-update-synology.sh` helper compares the public `VERSION` on `main` with the deployed image and can invoke the existing updater. It does not use `latest`. To opt in, copy it to the reference deployment's `deploy/` directory, make it executable, run a manual test, and configure exactly one DSM Task Scheduler job running as `root` every 30 minutes:

```sh
/bin/sh /volume1/docker/immich-google-sync/deploy/auto-update-synology.sh
```

Only enable the task after the manual test. A failed image pull should terminate before taking down the production container. This is an **optional** automated update workflow; deploying the GitHub files does not create a DSM task.

## Safe status checks

```sh
sudo docker ps --filter name=immich-google-sync --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
sudo docker logs --tail 40 immich-google-sync
```

Never expose `.env`, `token.json`, `credentials.json`, or operational secrets. See [installation](INSTALLATION.md), [OAuth](GOOGLE-OAUTH.md), and [security](../SECURITY.md).
