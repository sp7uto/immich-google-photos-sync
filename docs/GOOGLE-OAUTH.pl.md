# Google Photos OAuth — konfiguracja

[🇵🇱 Polski](GOOGLE-OAUTH.pl.md) · [🇬🇧 English](GOOGLE-OAUTH.md) · [Strona główna](../README.pl.md)

Aplikacja korzysta z zakresu OAuth `https://www.googleapis.com/auth/photoslibrary.appendonly` do dodawania nowych plików do Google Photos. Nie jest to uprawnienie do odczytu całej biblioteki.

## Projekt Google Cloud

1. Utwórz lub wybierz projekt w Google Cloud Console.
2. Włącz **Google Photos Library API**.
3. Skonfiguruj ekran zgody OAuth zgodnie z aktualnymi wymaganiami Google.
4. Utwórz klienta OAuth typu **Desktop application**.
5. Pobierz plik JSON klienta i zapisz go jako `credentials.json`.

Zasady weryfikacji, użytkowników testowych i publikacji aplikacji mogą się zmieniać — sprawdź aktualną dokumentację Google.

## Autoryzacja na komputerze z przeglądarką

Zrób to na zaufanym komputerze, nie w bezgłowym kontenerze:

```sh
python -m venv .venv
. .venv/bin/activate
pip install google-auth-oauthlib
python get_google_token.py
```

Podczas uruchamiania pomocnika `credentials.json` powinien znajdować się obok skryptu. Pomocnik otwiera przeglądarkę i zapisuje `token.json`. Przenieś **oba pliki** do prywatnego katalogu `data/` używanego przez Docker Compose. Nigdy nie umieszczaj ich w repozytorium.

## Ważne

- Token odświeżania może zostać unieważniony przez użytkownika lub Google.
- Panel aplikacji nie oferuje wbudowanej strony logowania do Google.
- Wysłane zdjęcia trafiają do biblioteki, nie automatycznie do wskazanego albumu.
- Zmiany ograniczeń API Google mogą wpływać na działanie; [oficjalne informacje Google](https://developers.google.com/photos/support/updates).
