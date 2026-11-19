# Instalacja — Immich → Google Photos Sync

[🇵🇱 Polski](INSTALLATION.pl.md) · [🇬🇧 English](INSTALLATION.md) · [Strona główna](../README.pl.md)

## Wymagania

- Docker Engine z Compose.
- Serwer Immich dostępny z kontenera, album źródłowy i klucz API z prawami odczytu albumu, zasobów i pobierania plików.
- Klient Google OAuth typu Desktop i autoryzowany token, zgodnie z [instrukcją OAuth](GOOGLE-OAUTH.pl.md).
- Zaufana sieć LAN, VPN albo tunel SSH do panelu WWW.

## Konfiguracja

```sh
git clone https://github.com/sp7uto/immich-google-photos-sync.git
cd immich-google-photos-sync
cp .env.example .env
mkdir -p data
```

Uzupełnij `.env`: `IMMICH_URL` (adres osiągalny **z kontenera**), `IMMICH_API_KEY` (tajny), `SOURCE_ALBUM` (domyślnie `do publikacji`), `TZ`, `PORT` (domyślnie 8787). Opcjonalne `PANEL_PASSWORD` włącza HTTP Basic w panelu i API. Nie szyfruje jednak połączenia — zdalnie stosuj HTTPS lub tunel.

Wygeneruj `credentials.json` i `token.json` zgodnie z instrukcją OAuth, po czym umieść je w prywatnym katalogu `data/`. Nie dodawaj sekretów do Git.

## Uruchomienie

```sh
docker compose up -d --build
docker compose logs --tail=100 immich-google-sync
```

Domyślne mapowanie portu: **127.0.0.1:8787** na hoście Docker. Panel lokalny: `http://localhost:8787`. Dostęp z innego komputera przez VPN, SSH lub proxy HTTPS z autoryzacją. Nie wystawiaj panelu publicznie.

## Opcjonalny kontener bez roota

Plik `docker-compose.nonroot.yml` włącza wybrany UID:GID, system plików root tylko do odczytu, usunięte capabilities, `no-new-privileges` i prywatny `/tmp`. Nie zmienia standardowej instalacji. Przed włączeniem zatrzymaj kontener, wykonaj kopię `data/` i sprawdź uprawnienia wybranego użytkownika do plików SQLite, `credentials.json` i `token.json`. Nie ustawiaj UID 1000 w ciemno, nie zmieniaj rekurencyjnie właścicieli plików. Użytkownik musi też móc atomowo zastąpić pliki tokenów i konfiguracji.

Ustaw lokalnie `APP_UID` i `APP_GID`, a następnie:

```sh
docker compose -f docker-compose.yml -f docker-compose.nonroot.yml config
docker compose -f docker-compose.yml -f docker-compose.nonroot.yml up -d --build
```

Powrót do pierwotnej konfiguracji:

```sh
docker compose -f docker-compose.yml up -d --force-recreate
```

To tryb opcjonalny, nie przetestowana procedura migracyjna. Większe pliki tymczasowo zajmują miejsce w `data/`.

## Wysyłanie zdjęć

W albumie Immich `do publikacji` umieść fotografie, zaznacz je w panelu i zatwierdź transfer. Zdjęcia są przesyłane do **biblioteki Google Photos**, bez przypisania do albumu docelowego. Nie jest potrzebny identyfikator albumu Google. Dostępne są historia CSV i kopia SQLite.

## Przerwane i niepewne wysyłki

Przed kontaktem z Google aplikacja oznacza zasób jako `uploading`. Po przerwaniu lub niejednoznacznym wyniku stan `uploading` albo `needs_review` blokuje automatyczne ponowienie. Panel wyświetla listę **Do weryfikacji** i jej eksport CSV.

**Nie kasuj wpisów SQLite na ślepo.** Najpierw sprawdź rzeczywistą bibliotekę Google Photos. Program nie ma automatycznej procedury uzgadniania.

Dostępne są dwie decyzje ręczne, wymagające dialogu i wpisania potwierdzenia:

- **Potwierdź wysłanie** — tylko jeśli zdjęcie istnieje w Google Photos, a jego prawdziwy identyfikator media item jest znany. Program zapisuje podany identyfikator, ale sam go nie sprawdza w Google.
- **Odblokuj ponowną wysyłkę** — tylko po wykluczeniu ryzyka duplikatu; zmienia stan na `error`, lecz **nie rozpoczyna automatycznie transferu**.

Podczas pracy kolejki decyzje są blokowane. Historia rozstrzygnięć znajduje się w `review_audit` i eksporcie **Decyzje CSV**. Jest to zapis operacyjny, a nie odporny na manipulacje dziennik audytu.

## Kopie i aktualizacje

Przycisk **Backup bazy** tworzy `/data/state-backup.db` przez prywatną migawkę SQLite i bezpieczne zastąpienie poprzedniej kopii; jest to jedna nadpisywana migawka, nie historia wersji. Wykonuj oddzielne kopie `data/`, w tym plików OAuth, z zachowaniem poufności.

Przed aktualizacją zachowaj kopię danych. Synology: [procedura produkcyjna](SYNOLOGY-PL.md). Publikacja nowej wersji na GitHubie nie jest równoznaczna z wdrożeniem na NAS.

## Ograniczenia

Bez dwukierunkowej synchronizacji, automatycznych albumów Google i publicznego callbacku OAuth. Hasło panelu jest opcjonalne; brak wbudowanego HTTPS. Wideo jest domyślnie wyłączone, a RAW wymaga testów.
