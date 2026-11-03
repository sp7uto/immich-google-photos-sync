# Release verification checklist

Use this checklist for **future releases**. The current version is shown in the repository's `VERSION` file; successful GitHub Actions checks and publication do not by themselves prove an end-to-end upload on every installation.

- [ ] Review the change scope and verify no secrets or private photos were committed.
- [ ] Run syntax, safety, Docker build and smoke checks.
- [ ] Check album discovery and preview against the deployed Immich version.
- [ ] Check OAuth refresh using a suitable test account when relevant.
- [ ] For upload-related changes, send one explicitly selected test photo and confirm its presence in the **Google Photos library**.
- [ ] Verify previously sent items remain protected against duplicates.
- [ ] Check pause/resume/cancel, CSV history, manual review and SQLite backup if those features changed.
- [ ] Ensure port 8787 is not publicly accessible.
- [ ] Publish a versioned GHCR image only after required checks pass.
- [ ] Deploy on Synology **manually** using `deploy/update-synology.sh vX.Y.Z`; verify service health and retain rollback materials.

## Current behavior and cautions

- Uploads are **one-way, manual-first**, and go to the Google Photos library; no automatic Google album assignment.
- Optional `PANEL_PASSWORD` enables HTTP Basic authentication; default Compose binds port 8787 to loopback.
- SQLite records `uploading` / `needs_review` protect uncertain transfers from automatic retry; investigate before requeueing.
- The queue runs in memory; interruptions can leave an item requiring manual verification.
- The app uses Google Photos `photoslibrary.appendonly` scope and does not read arbitrary Google Photos albums.
- Publishing a GitHub release **does not automatically update Synology**.

See [installation](INSTALLATION.md), [Google OAuth](GOOGLE-OAUTH.md), and [Synology operation](SYNOLOGY-PL.md).
