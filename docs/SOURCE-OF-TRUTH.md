# Source of truth and release policy

The **`main` branch of this GitHub repository** is the canonical public source tree.

An earlier locally distributed file named `immich-google-sync-github-ready.zip` was assembled before publication. Its contents **do not exactly match** the code committed to this repository and it is **superseded**. Do not mix files from that archive with files from `main`.

For a reproducible public snapshot, use GitHub's **Code → Download ZIP** or a `git clone` of this repository. The resulting files are taken from the same revision as the README and CI configuration.

## Versioning

- `main`: public development snapshot, not yet validated as a production release.
- `v3.0.0`: **not released**; do not create this tag until the release checklist passes.
- Synology: existing private deployment remains separate and has not been modified or verified against the public tree.

## Before a release

1. Record the exact Git commit SHA.
2. Run automated syntax and secret-filename checks.
3. Build and smoke-test the container from that SHA.
4. Verify the real Immich and Google Photos flows with disposable test media.
5. Inspect the public tree for secrets and personal data.
6. Publish release notes with the verified SHA and limitations.

See [release checklist](RELEASE-CHECKLIST.md).
