# 🐳 Docker installation

[🇬🇧 English](🐳-Installation) · [🇵🇱 Polski](🐳-Instalacja)

Requirements: Docker Compose, working Immich API and key, Google desktop OAuth credentials and token.

```sh
git clone https://github.com/sp7uto/immich-google-photos-sync.git
cd immich-google-photos-sync
cp .env.example .env
mkdir -p data
# Configure .env and OAuth credentials in data/ first.
docker compose up -d --build
```

The default panel binds to **127.0.0.1:8787**. Do not expose it directly to the internet.

**Read the canonical [installation guide](https://github.com/sp7uto/immich-google-photos-sync/blob/main/docs/INSTALLATION.md)** for environment variables, protected remote access, optional non-root Compose and recovery.
