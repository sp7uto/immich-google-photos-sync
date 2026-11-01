# Immich → Google Photos Sync — dokumentacja polska

**Wersja 3.0: ręczny wybór, świadome zatwierdzenie.**

Aplikacja uruchamiana w Dockerze pozwala wybrać zdjęcia z albumu Immich i przesłać je do biblioteki Google Photos. Nie jest to automatyczna, dwukierunkowa synchronizacja.

## Jak to działa

1. Utwórz w Immich album `Do Google Photos`.
2. Dodaj do niego fotografie przeznaczone do wysłania.
3. Otwórz panel aplikacji na porcie `8787` w zaufanej sieci.
4. Sprawdź miniatury i zaznacz zdjęcia.
5. Potwierdź wysyłkę i obserwuj postęp.

Program przechowuje historię wysyłek w lokalnej bazie SQLite. Umożliwia wstrzymanie i wznowienie kolejki oraz eksport historii do CSV.

## Ograniczenia

- Zdjęcia trafiają do biblioteki Google Photos, nie do konkretnego albumu Google.
- Token OAuth trzeba uzyskać osobnym skryptem.
- Panel nie ma własnego logowania ani HTTPS — **nie udostępniaj go publicznie**.
- Nie usuwa zdjęć z Immich.
- Obsługa dużych albumów, wideo i RAW wymaga dodatkowych testów.

Zobacz [instrukcję instalacji](INSTALLATION.md) oraz [OAuth](GOOGLE-OAUTH.md).
