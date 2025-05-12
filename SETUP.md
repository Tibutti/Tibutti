# Instrukcja wdrożenia automatycznego profilu GitHub

Ten projekt tworzy dynamiczny profil GitHub, który automatycznie aktualizuje się na podstawie Twojej aktywności i repozytoriów.

## Kroki wdrożenia

1. **Stwórz specjalne repozytorium profilowe**:
   - Utwórz nowe repozytorium na GitHub o nazwie dokładnie takiej samej jak Twoja nazwa użytkownika (w Twoim przypadku "Tibutti")
   - GitHub automatycznie rozpozna to jako specjalne repozytorium profilowe

2. **Skopiuj pliki z tego projektu**:
   - Skopiuj następujące pliki do swojego repozytorium profilowego:
     - `.github/workflows/update-readme.yml` (zapewnia automatyczne aktualizacje)
     - `scripts/update_readme.py` (skrypt generujący README)
     - `README.md` (wygenerowany plik README)

3. **Skonfiguruj GitHub Actions**:
   - Workflow jest już skonfigurowany, by używać domyślnego tokena `GITHUB_TOKEN`, który jest automatycznie dostępny w GitHub Actions
   - Nie są wymagane żadne dodatkowe ustawienia sekretu

4. **Weryfikacja działania**:
   - Po wgraniu plików do repozytorium, GitHub Actions powinien automatycznie uruchomić workflow
   - Powinieneś zobaczyć swój nowy profil automatycznie wygenerowany
   - Workflow działa codziennie o północy oraz przy każdym push do repozytorium (z wyjątkiem README.md)

## Dostosowanie projektu

Jeśli chcesz dostosować generowany profil:

1. **Edycja szablonu README**:
   - Otwórz plik `scripts/update_readme.py`
   - Znajdź funkcję `generate_readme` (około linia 215)
   - Dostosuj format, tekst wprowadzający i elementy w README

2. **Zmiana częstotliwości aktualizacji**:
   - W pliku `.github/workflows/update-readme.yml` zmień linię `cron: '0 0 * * *'`
   - Domyślnie aktualizuje się codziennie o północy
   - Możesz użyć [crontab.guru](https://crontab.guru/) aby stworzyć własny harmonogram

3. **Dodanie lub usunięcie elementów**:
   - Możesz dostosować wyświetlane języki, narzędzia i frameworki modyfikując:
     - `EXCLUDE_REPOS` - aby wykluczyć wybrane repozytoria
     - `EXCLUDE_LANGS` - aby wykluczyć określone języki
     - `MAX_LANG_DISPLAY` - aby zmienić maksymalną liczbę wyświetlanych języków

## Rozwiązywanie problemów

Jeśli profil nie aktualizuje się poprawnie:

1. Sprawdź logi w zakładce "Actions" w Twoim repozytorium
2. Upewnij się, że workflow ma uprawnienia do zapisu do repozytorium
3. Sprawdź, czy nazwa repozytorium dokładnie odpowiada Twojej nazwie użytkownika GitHub

## Użyte technologie

- Python (z bibliotekami: PyGithub, requests, pyyaml)
- GitHub Actions
- Shields.io do generowania ikon technologii
- GitHub API do pobierania statystyk i danych repozytoriów