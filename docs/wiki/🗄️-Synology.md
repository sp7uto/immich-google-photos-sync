# 🗄️ Synology deployment and recovery

[🇬🇧 English](🗄️-Synology) · [🇵🇱 Polski](🗄️-Synology-PL)

Synology deployments use Docker containers, persistent `data/` storage, OAuth credentials and SQLite state. Keep production and test databases separate.

A GitHub release **does not automatically upgrade** a running NAS container. The documented reference updater can make an SQLite backup and retain the previous container for rollback.

The optional DSM periodic update checker must be configured separately by the administrator. Never run two instances against the same production `/data`.

[Synology technical procedure](https://github.com/sp7uto/immich-google-photos-sync/blob/main/docs/SYNOLOGY.en.md)
