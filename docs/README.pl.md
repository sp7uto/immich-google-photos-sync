# Immich → Google Photos Sync — dokumentacja polska

**Wersja 3.0: ręczny wybór, świadome zatwierdzenie.**

Aplikacja uruchamiana w Dockerze pozwala wybrać zdjęcia z albumu Immich i przesłać je do biblioteki Google Photos. Nie jest to automatyczna, dwukierunkowa synchronizacja.

## Jak to działa

1. Utwórz w Immich album `do publikacji`.
2. Dodaj do niego fotografie przeznaczone do wysłania.
3. Otwórz panel aplikacji na porcie `8787` w zaufanej sieci.
4. Po sprawdzeniu, czy album docelowy już nie istnieje, użyj w panelu przycisku **Utwórz album Google Photos** i potwierdź utworzenie albumu `do publikacji`. Następnie sprawdź miniatury i zaznacz zdjęcia.
5. Potwierdź wysyłkę i obserwuj postęp.

Program przechowuje historię wysyłek w lokalnej bazie SQLite. Umożliwia wstrzymanie i wznowienie kolejki oraz eksport historii do CSV.

## Ograniczenia

- Zdjęcia są wysyłane do nowego albumu Google Photos `do publikacji`, utworzonego świadomie w panelu przez aplikację. Bez zapisanego identyfikatora albumu kolejka nie wystartuje. Jeśli tworzenie albumu zgłosi błąd, sprawdź Google Photos przed ponowieniem — album mógł powstać pomimo błędu zapisu lokalnego.
- Token OAuth trzeba uzyskać osobnym skryptem.
- Panel obsługuje opcjonalne hasło `PANEL_PASSWORD`, lecz nie zapewnia własnego HTTPS — **nie udostępniaj go publicznie**.
- Nie usuwa zdjęć z Immich.
- Obsługa dużych albumów, wideo i RAW wymaga dodatkowych testów.

Zobacz [instrukcję instalacji](INSTALLATION.md) oraz [OAuth](GOOGLE-OAUTH.md).
