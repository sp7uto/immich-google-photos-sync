# Changelog

## v3.1.4 — Official one-way icon

- Add official one-way Immich → Google Photos favicon and icon.
- Update English and Polish documentation to reflect confirmed v3.1.3 library-only uploads and manual Synology deployment.
- No changes to transfer logic, SQLite history, or Google Photos requests.

## v3.1.3 — Restore working library upload

- Remove mandatory Google Photos destination album ID from uploads.
- Preserve manual selection, transfer history, and duplicate protection.
- Confirmed successful photo transfer from Immich to Google Photos library on Synology (2026-11-03).


## v3.0 — Manual Select

- Select assets from an Immich source album.
- Preview images and explicitly approve uploads.
- Track sent files with local SQLite.
- Pause, resume and cancel the transfer queue.
- Export CSV history and create a state backup.

**Known limitations:** no Google album assignment; no built-in authentication for the local web panel.
