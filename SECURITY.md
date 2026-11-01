# Security

This service is designed for a **trusted LAN or VPN only**. Its Flask web interface supports optional HTTP Basic authentication via `PANEL_PASSWORD`, but has **no built-in TLS**. Do not expose port 8787 to the public internet.

## Protect credentials

- Keep `.env`, `data/token.json`, `data/credentials.json`, SQLite files and logs private. OAuth tokens created or refreshed by the application are written atomically with mode `0600`; existing files are not automatically chmodded.
- Use the default loopback-only Docker port binding. For remote access, use HTTPS through a trusted proxy or a secure tunnel; Basic authentication alone does not encrypt credentials.
- The configuration API rejects unknown keys and unsupported post-transfer actions.
- Use a minimally privileged Immich API key where practical.
- The Google Photos OAuth scope is `photoslibrary.appendonly`.
- Never commit credentials, tokens or actual local configuration.
- Review outbound transfers before confirming.

## Authentication attempt limits

When `PANEL_PASSWORD` is enabled, five failed authentication requests within 60 seconds temporarily block **all** panel access for 60 seconds (HTTP 429). This is an in-memory, single-process safeguard, not a distributed rate limiter. It can also be triggered by an attacker to deny access temporarily. Do not expose the service directly to the internet; use an authenticated HTTPS reverse proxy or secure tunnel. The counter resets on application restart.

## Reporting

Please report vulnerabilities privately to the repository maintainer instead of publishing exploitable details in an issue.

No formal security audit has been performed.
