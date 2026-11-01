# Immich → Google Photos Sync — dokumentacja polska

**Wersja 3.0: ręczny wybór, świadome zatwierdzenie.**

Aplikacja uruchamiana w Dockerze pozwala wybrać zdjęcia z albumu Immich i przesłać je do biblioteki Google Photos. Nie jest to automatyczna, dwukierunkowa synchronizacja.

## Jak to działa

1. Utwórz w Immich album `do publikacji`.
2. Dodaj do niego fotografie przeznaczone do wysłania.
3. Otwórz panel aplikacji na porcie `8787` w zaufanej sieci.
4. Sprawdź miniatury i zaznacz zdjęcia.
5. Potwierdź wysyłkę i obserwuj postęp.

Program przechowuje historię wysyłek w lokalnej bazie SQLite. Umożliwia wstrzymanie i wznowienie kolejki oraz eksport historii do CSV.

## Ograniczenia

- Docelowy album Google Photos ma nosić nazwę `do publikacji`, ale aktualny kod przesyła zdjęcia jedynie do biblioteki Google Photos. Przypisywanie do albumu docelowego nie jest jeszcze zaimplementowane.
- Token OAuth trzeba uzyskać osobnym skryptem.
- Panel obsługuje opcjonalne hasło `PANEL_PASSWORD`, lecz nie zapewnia własnego HTTPS — **nie udostępniaj go publicznie**.
- Nie usuwa zdjęć z Immich.
- Obsługa dużych albumów, wideo i RAW wymaga dodatkowych testów.

Zobacz [instrukcję instalacji](INSTALLATION.md) oraz [OAuth](GOOGLE-OAUTH.md).
