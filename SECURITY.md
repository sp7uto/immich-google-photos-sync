# Security

This service is designed for a **trusted LAN or VPN only**. Its Flask web interface has **no built-in authentication or TLS**. Do not expose port 8787 to the public internet.

## Protect credentials

- Keep `.env`, `data/token.json`, `data/credentials.json`, SQLite files and logs private.
- Use a minimally privileged Immich API key where practical.
- The Google Photos OAuth scope is `photoslibrary.appendonly`.
- Never commit credentials, tokens or actual local configuration.
- Review outbound transfers before confirming.

## Reporting

Please report vulnerabilities privately to the repository maintainer instead of publishing exploitable details in an issue.

No formal security audit has been performed.
