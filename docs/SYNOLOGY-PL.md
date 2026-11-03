# Immich → Google Photos Sync — instrukcja produkcyjna (Synology)

## Zasada działania

Aplikacja **nie synchronizuje automatycznie**. Użytkownik zaznacza fotografie w albumie Immich `do publikacji`, potwierdza wysyłkę i aplikacja przesyła wybrane zdjęcia do biblioteki Google Photos (bez automatycznego przypisania do albumu). Zdjęcia pozostają w Immich.

Wymagania: Docker, dostęp do Immich API, klucz Immich z uprawnieniami `album.read`, `asset.read`, `asset.view`, **`asset.download`**, OAuth Google z `photoslibrary.appendonly`.

## Aktualna instalacja DS1525+ (listopad 2026)

- Produkcja: kontener `immich-google-sync`, port hosta `8787`, dane `/volume1/docker/immich-google-sync/data`.
- Test: `immich-google-sync-test`, port `8788`, dane `/volume1/docker/immich-google-sync-test/data`; zatrzymany, zachowany do testów.
- Immich API: `http://192.168.1.225:8212`.
- Album źródłowy Immich: `do publikacji`; Google Photos: biblioteka, bez wymaganego albumu docelowego.
- Produkcyjny `state.db` jest niezależny od testowego. Nie kopiować testowej bazy na produkcję.
- Sekrety (`token.json`, `credentials.json`, plik `*.env`) **nie mogą trafić do GitHub**.

## Statusy i zapobieganie duplikatom

- `sent`: Google zwrócił identyfikator nowego zdjęcia; nie wysyłać ponownie.
- `uploading` / `needs_review`: wynik operacji niepewny; przed ponowieniem **sprawdzić Google Photos**.
- `error`: wpis dopuszczony do ponownej próby po świadomej weryfikacji.
- Wyczyść widok sesji: usuwa jedynie licznik i pamięciowy log ostatniej operacji, **nie dotyka SQLite**.
- `HTTP 403` przy pobieraniu oryginału z Immich: sprawdzić `asset.download`.
- `HTTP 403 ACCESS_TOKEN_SCOPE_INSUFFICIENT` przy odczycie albumu Google nie dowodzi awarii wysyłania: `appendonly` nie uprawnia do odczytu albumów.
- `HTTP 404` przy `mediaItems:batchCreate`: nie ponawiać automatycznie; surowa odpowiedź Google jest potrzebna do diagnozy, a zdjęcie mogło już trafić do biblioteki.

## Wydania i aktualizacje

1. Zmiany przechodzą przegląd i testy GitHub Actions; publikowany jest wersjonowany obraz `ghcr.io/sp7uto/immich-google-photos-sync:vX.Y.Z`.
2. Aktualizacja na Synology **nie jest automatyczna**. Wymaga świadomego uruchomienia skryptu z numerem opublikowanej wersji.
3. Aktualizator zachowuje poprzedni kontener i tworzy spójną migawkę SQLite przed przełączeniem. W razie nieudanego uruchomienia próbuje przywrócić poprzedni kontener.
4. Nie uruchamiać drugiej kopii z produkcyjnym `/data` i nie zastępować bazy produkcyjnej bazą testową.

## Weryfikacja bez ujawniania sekretów

```sh
sudo docker ps --filter name=immich-google-sync --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
sudo docker logs --tail 40 immich-google-sync
```

Panel produkcyjny: `http://192.168.1.225:8787` — dostęp tylko z zaufanej sieci. Bez `PANEL_PASSWORD` panel nie ma autoryzacji HTTP.

## Google Photos API

Od 31 marca 2025 r. Google ogranicza operacje odczytu do treści utworzonych przez aplikację. Zakres `photoslibrary.appendonly` wystarcza do tworzenia albumów i dodawania nowych zdjęć, ale nie do odczytywania albumów. Zobacz: https://developers.google.com/photos/support/updates

## Aktualizator na Synology

Skrypt [`deploy/update-synology.sh`](../deploy/update-synology.sh) jest używany do ręcznych aktualizacji produkcji. Sprawdza istniejący kontener, blokuje równoległe aktualizacje, zachowuje konfigurację i tokeny lokalnie, tworzy migawkę SQLite, pobiera wskazany obraz GHCR i kontroluje odpowiedź `/api/status`. W razie niepowodzenia próbuje przywrócić poprzedni kontener.

Uruchom na **Synology DS1525+** przez SSH (podstaw numer wydanej wersji):

```sh
sudo sh /volume1/docker/immich-google-sync/deploy/update-synology.sh vX.Y.Z
```

Skrypt wymaga istniejącego wolumenu `/volume1/docker/immich-google-sync/data`, portu 8787 i polityki restartu `unless-stopped`. Zachowany poprzedni kontener ma nazwę `immich-google-sync-before-update-<timestamp>`. Publikacja w GitHub nie uruchamia aktualizacji na NAS. Kontrola HTTP potwierdza start aplikacji, nie gwarantuje powodzenia kolejnego transferu do Google Photos.

## Automatyczne sprawdzanie aktualizacji (co 30 minut)

Skrypt [`deploy/auto-update-synology.sh`](../deploy/auto-update-synology.sh) odczytuje wersję z publicznego pliku `VERSION` na gałęzi `main`. Jeśli wersja różni się od obrazu uruchomionego kontenera, wywołuje istniejący `update-synology.sh`. **Nie używa tagu `latest`** i nie zmienia aplikacji ani danych samodzielnie. Jeśli obraz nowej wersji nie został jeszcze opublikowany, aktualizator przerwie działanie przed zatrzymaniem produkcji.

Jednorazowo umieść skrypt w `/volume1/docker/immich-google-sync/deploy/`, nadaj mu uprawnienia wykonywania i wykonaj test ręczny. Następnie w **DSM → Panel sterowania → Harmonogram zadań** utwórz *Zaplanowane zadanie → Skrypt zdefiniowany przez użytkownika*: użytkownik `root`, harmonogram co 30 minut, polecenie:

```sh
/bin/sh /volume1/docker/immich-google-sync/deploy/auto-update-synology.sh
```

Nie konfiguruj równocześnie drugiego zadania aktualizacji. Harmonogram DSM należy włączyć dopiero po poprawnym teście i upewnieniu się, że działająca wersja ma oczekiwany tag obrazu. Logi zadania można sprawdzać w Harmonogramie zadań. Zmiany w repozytorium nie instalują zadania DSM automatycznie.
