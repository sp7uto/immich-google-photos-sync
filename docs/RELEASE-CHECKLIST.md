# Release readiness checklist

This repository contains a public **source snapshot** of the manual-selection service. Do not label it a production-ready release until these checks pass.

- [ ] Confirm the public source matches the actual running deployment (review differences without exporting secrets).
- [ ] Run a clean Docker Compose build and verify the container starts.
- [ ] Check Immich album discovery and preview against a supported Immich version.
- [ ] Check Google OAuth consent and token refresh with a test account.
- [ ] Upload one explicitly selected disposable photo and verify it appears in Google Photos.
- [ ] Repeat the upload request and confirm duplicate handling.
- [ ] Check pause, resume, cancel, CSV history and database backup.
- [ ] Confirm no token, API key, local state or private photographs are tracked.
- [ ] Ensure port 8787 is not reachable from the public internet.
- [ ] Decide on version tag and release notes only after testing.

## Known technical caveats

- The panel has no authentication, and its API endpoints can trigger transfers.
- The compose example binds the port on all interfaces. Use a firewall or a trusted VPN/LAN.
- The worker starts in a background thread; an immediate second request may race the running flag.
- The queue state is in memory and is lost on restart.
- There is no upload retry/backoff for Google HTTP 429 or 5xx errors.
- A crash between a successful remote upload and the local SQLite commit may cause duplicates.
- Album lookup is not paginated.
- The `google_album` setting is currently informational and does not place media in a Google album.
- The Google Photos upload API remains supported with `photoslibrary.appendonly`; uploads and remote album creation must still be tested against current quotas and policies.

See [Google's official API update](https://developers.google.com/photos/support/updates) and [upload guide](https://developers.google.com/photos/library/guides/upload-media).
