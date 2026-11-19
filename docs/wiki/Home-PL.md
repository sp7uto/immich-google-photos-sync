# Immich → Google Photos Sync — Wiki

**[🇵🇱 Polski](https://github.com/sp7uto/immich-google-photos-sync/wiki/Home-PL) · [🇬🇧 English](https://github.com/sp7uto/immich-google-photos-sync/wiki/Home)**

![Grafika otwierająca](https://lh3.googleusercontent.com/pw/AP1GczOFyuxkUmxTsORsaXX6z2ky94-m6qMV_rm_fHo96uzQChurOYTJR8zOftdc5SgQ745nWGmuIxAoi5OX2zZPKinELqY59ku1EDk10si_CTlP4Baz5oBY=s1411-n-no)

**Twoje zdjęcia. Twój wybór. Twoja decyzja.**

Niezależna usługa Docker służąca do **ręcznego, jednokierunkowego** transferu wybranych zdjęć z Immich do **biblioteki Google Photos**. Oryginały pozostają w Immich. Każdą wysyłkę trzeba świadomie zatwierdzić.

## Dokumentacja

- [Opis projektu / README](https://github.com/sp7uto/immich-google-photos-sync/blob/main/README.pl.md)
- [Instalacja](https://github.com/sp7uto/immich-google-photos-sync/blob/main/docs/INSTALLATION.pl.md)
- [Google OAuth](https://github.com/sp7uto/immich-google-photos-sync/blob/main/docs/GOOGLE-OAUTH.pl.md)
- [Bezpieczeństwo](https://github.com/sp7uto/immich-google-photos-sync/blob/main/SECURITY.pl.md)
- [Synology — eksploatacja](https://github.com/sp7uto/immich-google-photos-sync/blob/main/docs/SYNOLOGY-PL.md)
- [Historia zmian](https://github.com/sp7uto/immich-google-photos-sync/blob/main/CHANGELOG.md)
- [English Wiki](https://github.com/sp7uto/immich-google-photos-sync/wiki/Home)

## Jak działa

1. Dodaj zdjęcia do albumu Immich `do publikacji`.
2. Obejrzyj je w lokalnym panelu WWW (domyślnie localhost:8787).
3. Zaznacz zdjęcia i zatwierdź wysyłkę.
4. Obserwuj postęp i historię SQLite/CSV.
5. Niepewne transfery sprawdzaj w Google Photos przed ponowieniem.

![Ręczny wybór fotografii](https://lh3.googleusercontent.com/pw/AP1GczMUBirbcJRiuUbSyVrv8e06zZLMWNNODuSf2ysG_JHYbZ4DDgWliS3VCKEzv0EBgd98vyV5F-RJ_q9x2eXdupkoEKFj1zvh3YgtLTpVDfQ66g0At-d5=s1411-n-no)

## Ważne

Program nie przypisuje zdjęć automatycznie do albumów Google, nie usuwa oryginałów i nie synchronizuje w obie strony. Panel nie ma własnego TLS — stosuj zaufaną sieć, VPN lub zabezpieczone proxy. Tokeny OAuth przechowuj prywatnie. Nie wykonano formalnego audytu bezpieczeństwa.

Pełny szybki start i spis dokumentacji zawiera [README](https://github.com/sp7uto/immich-google-photos-sync/blob/main/README.pl.md).

![Grafika końcowa](https://lh3.googleusercontent.com/pw/AP1GczOdZak7C7uZuOD717B6_A_k-ivTrg4ONLaivtfLTEjXupgvEqJdDBpV3zKVu1pAhKXWiOmYe18GxvhPIVaV_IWwfhYFD24cg4zedowT0QV-uQvlQHhr=s1411-n-no)
