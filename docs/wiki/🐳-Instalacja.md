# 🐳 Instalacja w Dockerze

[🇵🇱 Polski](🐳-Instalacja) · [🇬🇧 English](🐳-Installation)

Wymagania: Docker Compose, działające API Immich i klucz oraz dane i token klienta Google OAuth typu Desktop.

```sh
git clone https://github.com/sp7uto/immich-google-photos-sync.git
cd immich-google-photos-sync
cp .env.example .env
mkdir -p data
# Najpierw skonfiguruj .env i pliki OAuth w data/.
docker compose up -d --build
```

Panel domyślnie nasłuchuje na **127.0.0.1:8787**. Nie udostępniaj go bezpośrednio w internecie.

Pełne informacje o zmiennych, bezpiecznym dostępie zdalnym, wariancie bez roota i przywracaniu znajdziesz w [instrukcji instalacji](https://github.com/sp7uto/immich-google-photos-sync/blob/main/docs/INSTALLATION.pl.md).
