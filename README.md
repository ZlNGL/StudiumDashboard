# Studium Dashboard

Ein Dashboard zur Überwachung des akademischen Fortschritts, mit Fokus auf Notendurchschnitt und ECTS-Credits.

## Projektbeschreibung
Diese Anwendung ermöglicht (Studierenden):
- Kontrolle des Notendurchschnitts und Zielerreichung
- ECTS-Fortschrittsverfolgung
- Visuelle Darstellung von Noten und Leistungen
- Verwaltung von Modulen, Semestern und Prüfungen

## Installation
```bash
git clone https://github.com/ZlNGL/studium-dashboard.git
cd studium-dashboard
python -m venv venv                 # Optional
source venv/bin/activate            # Unix/macOS
# oder venv\Scripts\activate        # Windows
pip install -r requirements.txt
python main.py
```

## Projektstruktur
```
studium-dashboard/
├── models/                 # Modellklassen (Student, Modul, etc.)
├── controllers/            # Controller-Klassen
├── views/                  # View-Klassen
├── tests/                  # Testfälle
│   ├── models/             # Tests für Modellklassen
│   ├── controllers/        # Tests für Controller
│   └── run_tests.py        # Test-Runner
├── main.py                 # Haupteinstiegspunkt
└── data/                   # Daten und Grafiken
```

## Schnellstart
1. Starten Sie die Anwendung mit `python main.py`
2. Wählen Sie "j" für Beispieldaten oder "n" für eigene Eingaben
3. Nutzen Sie das Hauptmenü für Funktionen wie Notendurchschnitt anzeigen, Prüfungen erfassen oder Daten exportieren

## Features
- **Notenverwaltung**: Nachverfolgung von Noten und Prüfungen mit Zielvorgaben.
- **Fortschrittsverfolgung**: Visualisierung des ECTS-Fortschritts und der Semesterleistungen.
- **Datenimport/-export**: CSV-basierter In-/Export für Datensicherung und Datenübertragung.

## Tests ausführen
```bash
# Alle Tests ausführen
python -m tests.run_tests

# Bestimmte Tests ausführen
python -m tests.run_tests tests.models.test_student

```

## Fehlerbehebung
- **Installationsprobleme**: Stellen Sie sicher, dass Python 3.6+ installiert ist.
- **Fehlende Diagramme**: Verzeichnis 'data/grafiken' muss existieren und beschreibbar sein.
- **Dateifehler**: Bei JSON-Dateifehlern, löschen Sie bitte die 'data/studium_data.json' Datei und starten Sie anschließend neu.