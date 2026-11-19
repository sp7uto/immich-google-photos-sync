# 🔐 Bezpieczeństwo i OAuth

[🇵🇱 Polski](🔐-Bezpieczeństwo) · [🇬🇧 English](🔐-Security)

Pliki `.env`, `data/token.json`, `data/credentials.json`, bazę SQLite i logi przechowuj prywatnie.

- Otwieraj panel tylko w zaufanej sieci LAN/VPN lub przez tunel albo proxy HTTPS z autoryzacją.
- HTTP Basic przez `PANEL_PASSWORD` jest opcjonalne, lecz samo nie szyfruje połączenia.
- Brak wbudowanego TLS. Nie wystawiaj portu 8787 bezpośrednio do internetu.
- Google OAuth używa `photoslibrary.appendonly` do dodawania zdjęć, nie do odczytu całej biblioteki.
- Nie wykonano formalnego audytu bezpieczeństwa.

[Zasady bezpieczeństwa](https://github.com/sp7uto/immich-google-photos-sync/blob/main/SECURITY.pl.md) · [Konfiguracja OAuth](https://github.com/sp7uto/immich-google-photos-sync/blob/main/docs/GOOGLE-OAUTH.pl.md)
