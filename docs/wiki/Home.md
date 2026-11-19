# Immich → Google Photos Sync — Wiki

**[🇬🇧 English](Home.md) · [🇵🇱 Polski](Home-PL.md)**

![Header](https://lh3.googleusercontent.com/pw/AP1GczOFyuxkUmxTsORsaXX6z2ky94-m6qMV_rm_fHo96uzQChurOYTJR8zOftdc5SgQ745nWGmuIxAoi5OX2zZPKinELqY59ku1EDk10si_CTlP4Baz5oBY=s1411-n-no)

**Your photos. Your selection. Your approval.**

A self-hosted Docker service for **manual, one-way** transfer of selected Immich photos to the **Google Photos library**. Originals stay on Immich. An operator explicitly chooses and approves each batch.

## Guides

- [Project overview / README](../../README.md)
- [Installation](../INSTALLATION.md)
- [Google OAuth](../GOOGLE-OAUTH.md)
- [Security](../../SECURITY.md)
- [Synology operations](../SYNOLOGY.en.md)
- [Change history](../../CHANGELOG.md)
- [Polish Wiki / Wiki po polsku](Home-PL.md)

## Workflow

1. Add intended images to Immich album `do publikacji`.
2. Review the local web panel (default localhost:8787).
3. Select photos and explicitly approve sending.
4. Monitor progress and examine SQLite/CSV history.
5. Review uncertain uploads against Google Photos before a retry.

![Manual selection](https://lh3.googleusercontent.com/pw/AP1GczMUBirbcJRiuUbSyVrv8e06zZLMWNNODuSf2ysG_JHYbZ4DDgWliS3VCKEzv0EBgd98vyV5F-RJ_q9x2eXdupkoEKFj1zvh3YgtLTpVDfQ66g0At-d5=s1411-n-no)

## Important notes

The program does not assign destination albums, delete originals, or sync in both directions. The web panel has no built-in TLS; restrict it to trusted networks, VPN or a secure proxy. Keep OAuth credentials private. No formal security audit has been conducted.

See the main [README](../../README.md) for the exact quick start and all documentation links.

![Footer](https://lh3.googleusercontent.com/pw/AP1GczOdZak7C7uZuOD717B6_A_k-ivTrg4ONLaivtfLTEjXupgvEqJdDBpV3zKVu1pAhKXWiOmYe18GxvhPIVaV_IWwfhYFD24cg4zedowT0QV-uQvlQHhr=s1411-n-no)
