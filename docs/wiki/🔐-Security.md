# 🔐 Security and OAuth

[🇬🇧 English](🔐-Security) · [🇵🇱 Polski](🔐-Bezpieczeństwo)

Keep `.env`, `data/token.json`, `data/credentials.json`, SQLite files, and logs private.

- Access the panel only from a trusted LAN/VPN or through an authenticated HTTPS proxy/tunnel.
- HTTP Basic via `PANEL_PASSWORD` is optional; it does not provide encryption.
- The application has no built-in TLS. Never publish the panel's port 8787 directly.
- Google OAuth uses `photoslibrary.appendonly` for uploads, not full-library reading.
- No formal security audit has been performed.

[Security reference](https://github.com/sp7uto/immich-google-photos-sync/blob/main/SECURITY.md) · [OAuth setup](https://github.com/sp7uto/immich-google-photos-sync/blob/main/docs/GOOGLE-OAUTH.md)
