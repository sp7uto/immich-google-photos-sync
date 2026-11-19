# Bezpieczeństwo — Immich → Google Photos Sync

[🇵🇱 Polski](SECURITY.pl.md) · [🇬🇧 English](SECURITY.md) · [Strona główna](README.pl.md)

Usługa jest przeznaczona **wyłącznie do zaufanej sieci LAN lub VPN**. Panel Flask obsługuje opcjonalne HTTP Basic przez `PANEL_PASSWORD`, ale **nie ma wbudowanego TLS**. Nie wystawiaj portu 8787 bezpośrednio do internetu.

## Ochrona danych i sekretów

- Chroń `.env`, `data/token.json`, `data/credentials.json`, SQLite i logi.
- Nowo utworzone lub odświeżone tokeny OAuth są zapisywane atomowo z trybem `0600`; istniejące pliki nie są automatycznie poddawane `chmod`.
- Pozostaw domyślne mapowanie portu wyłącznie na `127.0.0.1`.
- Do zdalnego dostępu używaj bezpiecznego tunelu albo proxy HTTPS i autoryzacji. HTTP Basic bez szyfrowania nie chroni haseł.
- API konfiguracji odrzuca nieznane klucze i nieobsługiwane akcje po transferze.
- Używaj możliwie najmniejszych wymaganych uprawnień klucza Immich.
- Zakres Google Photos OAuth to `photoslibrary.appendonly`.
- Nie zapisuj prawdziwych tokenów ani lokalnej konfiguracji w GitHubie.
- Zawsze sprawdzaj wybór zdjęć przed wysłaniem.

## Ograniczanie prób logowania

Po włączeniu `PANEL_PASSWORD` pięć nieudanych żądań autoryzacji w ciągu 60 sekund blokuje na 60 sekund **cały panel** (HTTP 429). To licznik w pamięci jednego procesu, nie rozproszony system ochrony. Może zostać wykorzystany do czasowego zablokowania dostępu. Po restarcie aplikacji licznik się zeruje.

## Zgłaszanie podatności

Prosimy o prywatny kontakt z opiekunem repozytorium zamiast publikowania szczegółów umożliwiających wykorzystanie podatności w publicznych Issues.

**Nie przeprowadzono formalnego audytu bezpieczeństwa.**
