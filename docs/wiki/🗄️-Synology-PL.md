# 🗄️ Synology — wdrażanie i przywracanie

[🇵🇱 Polski](🗄️-Synology-PL) · [🇬🇧 English](🗄️-Synology)

Instalacja na Synology korzysta z kontenerów Docker, trwałego katalogu `data/`, sekretów OAuth i stanu SQLite. Bazy produkcyjna i testowa muszą pozostać oddzielne.

Wydanie na GitHubie **nie aktualizuje automatycznie** kontenera NAS. Opisany aktualizator tworzy kopię SQLite i zachowuje poprzedni kontener do przywrócenia.

Opcjonalny harmonogram kontroli aktualizacji w DSM wymaga osobnej konfiguracji. Nie uruchamiaj dwóch instancji na tym samym produkcyjnym `/data`.

[Pełna instrukcja Synology](https://github.com/sp7uto/immich-google-photos-sync/blob/main/docs/SYNOLOGY-PL.md)
