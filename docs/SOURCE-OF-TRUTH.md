# Source of truth and release policy

The `main` branch is the canonical public source. The current intended release version is in [`VERSION`](../VERSION); release images use the immutable version tag `ghcr.io/sp7uto/immich-google-photos-sync:vX.Y.Z`.

The older local archive `immich-google-sync-github-ready.zip` predates publication and is superseded. Do not mix its contents with the current repository.

## Source, release and deployment

- **GitHub main:** current source and documentation.
- **GitHub Actions / GHCR:** build and publish versioned Docker images after validation.
- **Synology DS1525+:** separate running installation; publishing code or an image does **not** update it.
- **Manual update:** `sudo sh /volume1/docker/immich-google-sync/deploy/update-synology.sh vX.Y.Z`, with a real published version number. The script snapshots SQLite and retains the previous container for rollback.

Version numbers are displayed by the application and are **not embedded in the icon**.

## Verified scope

On 2026-11-03 a selected photo was confirmed uploaded from Immich to the Google Photos **library** after the v3.1.3 fix. Later visual releases do not change upload logic. This is a confirmed transfer, not a blanket guarantee for every future upload or deployment.

For future releases, follow the [release verification checklist](RELEASE-CHECKLIST.md) and [Synology instructions](SYNOLOGY-PL.md).
