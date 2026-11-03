# Immich → Google Photos Sync — instrukcja produkcyjna (Synology)

## Zasada działania

Aplikacja **nie synchronizuje automatycznie**. Użytkownik zaznacza fotografie w albumie Immich `do publikacji`, potwierdza wysyłkę i aplikacja tworzy elementy w albumie Google Photos utworzonym przez tę aplikację. Zdjęcia pozostają w Immich.

Wymagania: Docker, dostęp do Immich API, klucz Immich z uprawnieniami `album.read`, `asset.read`, `asset.view`, **`asset.download`**, OAuth Google z `photoslibrary.appendonly`.

## Aktualna instalacja DS1525+ (listopad 2026)

- Produkcja: kontener `immich-google-sync`, port hosta `8787`, dane `/volume1/docker/immich-google-sync/data`.
- Test: `immich-google-sync-test`, port `8788`, dane `/volume1/docker/immich-google-sync-test/data`; zatrzymany, zachowany do testów.
- Immich API: `http://192.168.1.225:8212`.
- Album źródłowy i docelowy: `do publikacji`.
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

## Wydania i aktualizacje podobne do IRR

1. Zmiany trafiają na gałąź i przechodzą przegląd oraz testy.
2. Tag wersji `vX.Y.Z` uruchamia GitHub Actions, który buduje i publikuje obraz w GHCR (`ghcr.io/sp7uto/immich-google-photos-sync:vX.Y.Z`).
3. Synology pobiera **wyłącznie zatwierdzoną wersję**, nie `latest`; nie przełączać produkcji automatycznie na nieprzetestowany commit.
4. Przed aktualizacją zachować obraz poprzedniej wersji, `docker inspect` i spójną migawkę SQLite, oraz niezmienione tokeny i konfigurację.
5. Najpierw test na porcie 8788 z osobną bazą; dopiero po udanym teście wdrożenie na 8787 z istniejącym wolumenem produkcyjnym.
6. W przypadku awarii wrócić do poprzedniego obrazu z **tym samym** wolumenem produkcyjnym, chyba że migracja bazy wymaga przywrócenia kopii.

**Ważne:** sam workflow publikowania obrazu nie aktualizuje NAS. Do automatycznego wdrożenia na wzór IRR potrzebny jest osobny, przetestowany skrypt i timer na Synology. Nie wolno go włączać przed potwierdzeniem poprawnego rollbacku.

## Weryfikacja bez ujawniania sekretów

```sh
sudo docker ps --filter name=immich-google-sync --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
sudo docker logs --tail 40 immich-google-sync
```

Panel produkcyjny: `http://192.168.1.225:8787` — dostęp tylko z zaufanej sieci. Bez `PANEL_PASSWORD` panel nie ma autoryzacji HTTP.

## Google Photos API

Od 31 marca 2025 r. Google ogranicza operacje odczytu do treści utworzonych przez aplikację. Zakres `photoslibrary.appendonly` wystarcza do tworzenia albumów i dodawania nowych zdjęć, ale nie do odczytywania albumów. Zobacz: https://developers.google.com/photos/support/updates

## Aktualizator na Synology (przygotowany, jeszcze niewdrożony)

Skrypt [`deploy/update-synology.sh`](../deploy/update-synology.sh) wykonuje **jednorazową aktualizację wskazanej wersji**: kontrola kontenera, blokada współbieżności, backup SQLite, zachowanie `docker inspect`, pobranie obrazu GHCR, uruchomienie z istniejącym `/data`, kontrola `/api/test`, przy błędzie przywrócenie poprzedniego kontenera. Nie nadpisuje bazy podczas rollbacku.

Przykład **dopiero po opublikowaniu i przetestowaniu wydania**:

```sh
sudo sh deploy/update-synology.sh v3.1.0
```

Skrypt zakłada aktualny port 8787, istniejący wolumen i politykę restartu `unless-stopped`. W razie różnic kończy działanie bez wdrożenia. Nie jest jeszcze uruchamiany na NAS i nie ma timera. **Nie uruchamiać go z gałęzi roboczej ani przed testem odtwarzania.** Test HTTP `/api/test` jest testem uruchomienia, nie gwarantuje skutecznego przesyłania do Google.

Zachowany poprzedni kontener ma nazwę `immich-google-sync-before-update-<timestamp>`; nie usuwać go przed zatwierdzeniem nowej wersji. Zmiany w danych podczas działania nowej wersji nie są automatycznie cofane.
