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
- `SOURCE_ALBUM`: source album name (default: `Do Google Photos`)
- `TZ`: timezone
- `PORT`: Flask application port (default: 8787)

Generate `token.json` with the [OAuth guide](GOOGLE-OAUTH.md). Put `credentials.json` and `token.json` in `data/`. Protect the directory.

## Start

```bash
docker compose up -d --build
docker compose logs --tail=100 immich-google-sync
```

By default the Compose file binds port 8787 to **127.0.0.1** on the Docker host, so open `http://localhost:8787` locally. To reach the panel remotely, use an SSH tunnel or an authenticated reverse proxy over a trusted network. The panel has no authentication; **do not expose it publicly**. If you deliberately change the Compose bind address to a LAN IP, restrict access using a firewall.

## Operation

Create an Immich album named as `SOURCE_ALBUM`, manually add images, preview and select them in the panel, then confirm transfer. CSV history and SQLite backup are available in the interface.

## Backup and upgrade

Back up `data/` securely, including the SQLite database and OAuth token. Before upgrades, stop the container and retain a backup. Do not publish or commit your real `.env` or `data/`.

## Limitations

The Google album setting is not applied to remote albums in v3.0. The application does not provide a public OAuth callback or an authenticated web panel.
