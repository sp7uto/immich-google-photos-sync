# Installation

## Requirements

- Docker Engine with Compose
- Reachable Immich server and an Immich API key
- Google Cloud OAuth desktop client credentials and an authorized token
- Trusted LAN or VPN access to the local web panel

## Configure

```bash
cp .env.example .env
mkdir -p data
```

Edit `.env`:

- `IMMICH_URL`: Immich URL reachable **from the container**
- `IMMICH_API_KEY`: Immich API key (keep secret)
- `SOURCE_ALBUM`: source album name (default: `do publikacji`)
- `TZ`: timezone
- `PORT`: Flask application port (default: 8787)
- `PANEL_PASSWORD`: optional strong password enabling HTTP Basic authentication on all panel/API routes. Without it, the panel is unauthenticated; keep the default loopback-only binding. Basic authentication must be used only over HTTPS or a protected tunnel when accessing remotely.

Generate `token.json` with the [OAuth guide](GOOGLE-OAUTH.md). Put `credentials.json` and `token.json` in `data/`. Protect the directory.

## Start

```bash
docker compose up -d --build
docker compose logs --tail=100 immich-google-sync
```

By default the Compose file binds port 8787 to **127.0.0.1** on the Docker host, so open `http://localhost:8787` locally. To reach the panel remotely, use an SSH tunnel or an authenticated reverse proxy over a trusted network. The panel supports optional Basic authentication, but has no built-in TLS; **do not expose it publicly**. If you deliberately change the Compose bind address to a LAN IP, restrict access using a firewall.

## Optional non-root container hardening

An opt-in `docker-compose.nonroot.yml` override runs the service under an explicitly chosen UID:GID, with a read-only root filesystem, dropped Linux capabilities, `no-new-privileges`, and a small private `/tmp` mount. **The standard Compose setup remains unchanged.**

Before using the override, stop the service, back up `data/`, and identify a host UID:GID that already has read/write access to the existing `data/` directory and SQLite files, plus read access to `credentials.json` and `token.json`. The service must also be able to create temporary files and atomically replace `token.json` and `config.json` in `data/`. Do not change file ownership recursively or assume UID 1000 is correct. In particular, existing mode `0600` token files must be owned by the chosen UID or otherwise readable by it.

After checking these prerequisites, set `APP_UID` and `APP_GID` in your local `.env`, then explicitly opt in:

```bash
docker compose -f docker-compose.yml -f docker-compose.nonroot.yml config
docker compose -f docker-compose.yml -f docker-compose.nonroot.yml up -d --build
```

For rollback to the original root-running configuration, remove the override from the command:

```bash
docker compose -f docker-compose.yml up -d --force-recreate
```

This is an optional deployment mode, not a tested migration procedure. It does not modify existing file ownership or secrets. Large uploads are temporarily staged in `data/`, so sufficient writable disk space is required.

## Operation

The source Immich album and destination Google Photos album are both named `do publikacji`. Before the first transfer, use **Utwórz album Google Photos** in the panel, after checking that a duplicate album does not already exist. The action requires a typed confirmation and creates an **app-owned** Google Photos album; its ID is saved in `data/config.json`. Uploads use that ID in `mediaItems.batchCreate`. Until an ID is saved, the transfer queue refuses to start. Google restricts album management to app-created content. If album creation fails or its result cannot be saved, **check Google Photos before retrying**: a remote album might have been created even if the local ID was not recorded. Renaming the configured album in the application is blocked to avoid an ID/name mismatch.


Create an Immich album named as `SOURCE_ALBUM`, manually add images, preview and select them in the panel, then confirm transfer. CSV history and SQLite backup are available in the interface.

## Interrupted or uncertain transfers

Before contacting Google Photos, the application records the asset as `uploading` in SQLite. If the process stops unexpectedly, or an upload raises an error after the transfer starts, the item remains blocked from automatic retry (`uploading` or `needs_review`). The preview shows these items under **Do weryfikacji**, separately from **Nowe** and successfully sent items. The **Do weryfikacji CSV** download provides asset IDs, filenames, timestamps, status and recorded errors without modifying transfer state.

**Do not delete or edit these database records blindly.** Inspect the actual Google Photos library and the local CSV history before deciding what to do. The application currently has no automated reconciliation or explicit requeue operation for uncertain items. A failed transfer may not have created a Google item at all; the conservative block prevents accidental duplicates but may require manual recovery. Existing `error` records from older versions remain retryable.

### Manual resolution

For a flagged asset, inspect Google Photos independently. The panel offers two explicit choices, each requiring a confirmation dialog and a typed confirmation string:

- **Potwierdź wysłanie**: use only when the asset was verified as present in Google Photos **and its actual Google media item ID is known**. The application records that ID and marks the asset as sent; it does not verify the ID against Google.
- **Odblokuj ponowną wysyłkę**: use only when you have independently established that retrying will not create a duplicate. The asset is marked retryable (`error`); **no upload starts automatically**. Select and confirm it separately later.

Resolution is refused while a transfer queue is running. The operation does not delete Immich or Google Photos media. Review decisions are stored in a separate SQLite `review_audit` table in the same transaction as the status update. The **Decyzje CSV** link exports the decision history, including the previous status and any manually supplied Google media item ID. This is a durable operational record, **not** a tamper-proof audit log. Back up SQLite before manual reconciliation.


## Backup and upgrade

The **Backup bazy** panel action writes `/data/state-backup.db` through a private (`0600`) temporary SQLite backup and replaces the previous backup only after the copy completes. The previous backup remains intact if the copy fails before replacement. This is a single rolling snapshot, not a versioned backup history.



Back up `data/` securely, including the SQLite database and OAuth token. Before upgrades, stop the container and retain a backup. Do not publish or commit your real `.env` or `data/`.

## Limitations

The Google album setting is not applied to remote albums in v3.0. The application does not provide a public OAuth callback. Panel authentication is optional via `PANEL_PASSWORD`.
