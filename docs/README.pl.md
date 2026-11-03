# Immich → Google Photos Sync — dokumentacja polska

![Oficjalna ikona transferu jednokierunkowego](../app/static/icon.svg)

**Wersja 3.1.5: ręczny wybór, świadome zatwierdzenie, oficjalna ikona.**

Aplikacja uruchamiana w Dockerze pozwala wybrać zdjęcia z albumu Immich i przesłać je do biblioteki Google Photos. Nie jest to automatyczna, dwukierunkowa synchronizacja.

## Jak to działa

1. Utwórz w Immich album `do publikacji`.
2. Dodaj do niego fotografie przeznaczone do wysłania.
3. Otwórz panel aplikacji na porcie `8787` w zaufanej sieci.
4. Sprawdź miniatury i zaznacz zdjęcia. Przesyłanie trafia do **biblioteki Google Photos**, bez automatycznego przypisywania do albumu.
5. Potwierdź wysyłkę i obserwuj postęp.

Program przechowuje historię wysyłek w lokalnej bazie SQLite. Umożliwia wstrzymanie i wznowienie kolejki oraz eksport historii do CSV.

## Ograniczenia

- Zdjęcia trafiają do biblioteki Google Photos, nie do konkretnego albumu. Nie jest wymagany identyfikator albumu Google.
- Token OAuth trzeba uzyskać osobnym skryptem.
- Panel obsługuje opcjonalne hasło `PANEL_PASSWORD`, lecz nie zapewnia własnego HTTPS — **nie udostępniaj go publicznie**.
- Nie usuwa zdjęć z Immich.
- Obsługa dużych albumów, wideo i RAW wymaga dodatkowych testów.

Zobacz [instrukcję instalacji](INSTALLATION.md) oraz [OAuth](GOOGLE-OAUTH.md).

## Aktualizacje Synology

Publikacja nowej wersji w GitHub **nie aktualizuje automatycznie** działającego kontenera. Aktualizacja jest uruchamiana świadomie poleceniem `sudo sh /volume1/docker/immich-google-sync/deploy/update-synology.sh v3.1.5`. Skrypt wykonuje kopię SQLite i zachowuje poprzedni kontener do wycofania aktualizacji.
