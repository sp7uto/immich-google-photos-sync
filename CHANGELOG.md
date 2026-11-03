# Changelog

## v3.1.6 — Clean, version-independent branding

- Refine the SVG icon to remove the visible petal artifacts and retain one forward arrow.
- Keep version numbers out of the image; panel version is rendered dynamically, and the README release badge follows GitHub releases.
- No transfer or database changes.


## v3.1.5 — Branded one-way icon in the panel

- Replace generic photo pictogram with a five-petal Immich-style mark next to the Google Photos pinwheel, connected by one directional arrow.
- Display the app icon directly in the panel heading as well as the browser favicon and documentation.
- No changes to upload, authentication, queue or database behavior.


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
