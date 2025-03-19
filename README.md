# Studium Dashboard

Ein umfassendes Dashboard zur Überwachung des akademischen Fortschritts, mit Fokus auf die Kontrolle des Notendurchschnitts und der ECTS-Credits.

## Projektbeschreibung

Dieses Dashboard ermöglicht es Studierenden, ihren akademischen Fortschritt zu verfolgen, wobei der Fokus auf:
- Notendurchschnitt-Überwachung mit Zielerreichung
- ECTS-Fortschrittsverfolgung
- Visuelle Darstellung von Noten und Fortschritt
- Verwaltung von Modulen, Semestern und Prüfungen
liegt.

Die Anwendung ist nach dem Model-View-Controller-Muster konzipiert, wodurch eine saubere Trennung der Zuständigkeiten und Wartbarkeit gewährleistet wird.

## GitHub Repository

Der vollständige Quellcode für dieses Projekt ist auf GitHub verfügbar:
[https://github.com/ZlNGL/studium-dashboard](https://github.com/ZlNGL/studium-dashboard)

## Installationsanleitung

### Voraussetzungen
- Python 3.6 oder höher
- matplotlib Bibliothek

### Schritt 1: Repository klonen
```bash
git clone https://github.com/ZlNGL/studium-dashboard.git
cd studium-dashboard
```

### Schritt 2: Virtuelle Umgebung erstellen (optional, aber empfohlen)
#### Unter Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### Unter macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Schritt 3: Abhängigkeiten installieren
```bash
pip install matplotlib
```
oder
```bash
pip install -r requirements.txt
```

### Schritt 4: Anwendung starten
```bash
python main.py
```

## Projektstruktur
```
studium-dashboard/
├── models/                 # Enthält alle Modellklassen
│   ├── __init__.py         # Macht Modellklassen importierbar
│   ├── person.py           # Basisklasse für Personen
│   ├── student.py          # Erweiterung von Person für Studenten
│   ├── note.py             # Repräsentiert eine Note
│   ├── pruefungsleistung.py # Repräsentiert eine Prüfungsleistung
│   ├── modul.py            # Repräsentiert ein Modul
│   ├── semester.py         # Repräsentiert ein Semester
│   └── studiengang.py      # Repräsentiert einen Studiengang
├── controllers/            # Enthält Controller-Klassen
│   ├── __init__.py         # Macht Controller-Klassen importierbar
│   ├── datenmanager.py     # Verwaltet Datenpersistenz
│   └── dashboard.py        # Hauptcontroller der Anwendung
├── views/                  # Enthält View-Klassen
│   ├── __init__.py         # Macht View-Klassen importierbar
│   ├── dashboard_visualisierung.py # Erstellt Visualisierungen
│   └── benutzer_interaktion.py    # Verwaltet Benutzerinteraktion
├── main.py                 # Haupteinstiegspunkt der Anwendung
├── requirements.txt        # Liste der Abhängigkeiten
└── data/                   # Verzeichnis für Daten und Grafiken
    ├── studium_data.json   # Gespeicherte Anwendungsdaten
    └── grafiken/           # Generierte Diagramme und Visualisierungen
```

## Schnellstart

Bei der ersten Ausführung der Anwendung werden Sie gefragt, ob Sie Beispieldaten erstellen oder eigene Daten eingeben möchten:

1. **Beispieldaten**: Wählen Sie "j", um einen Beispielstudenten mit Musterdaten zu erstellen
2. **Eigene Daten**: Wählen Sie "n", um Ihren eigenen Studenten und Studiengang zu erstellen

Anschließend können über das Hauptmenü verschiedene Funktionen genutzt werden:

- Notendurchschnitt und ECTS-Fortschritt anzeigen
- Notenverteilung und anstehende Prüfungen einsehen
- Neue Noten und Module erfassen
- Ziel-Notendurchschnitt bearbeiten
- Daten im CSV-Format ex- und importieren

## Features

- **Notenverfolgung**: Überwachen des aktuellen Notendurchschnitts im Vergleich zum Ziel-Notendurchschnitt
- **ECTS-Fortschritt**: Verfolgen der absolvierten ECTS-Credits und verbleibenden Anforderungen
- **Visuelle Diagramme**: Betrachten des Studium- Fortschritts und die Notenverteilung als Diagramme
- **Prüfungsverwaltung**: Erfassen und verfolgen von anstehenden Prüfungen
- **Modulverwaltung**: Organisieren der Kurse nach Semestern und verfolgen der Abschlüsse
- **Datenimport/-export**: Importieren und exportieren der Daten als CSV-Dateien

## Fehlerbehebung

- **Installationsprobleme**: Stellen Sie sicher, dass Python 3.6+ und pip korrekt installiert sind
- **Fehlende Diagramme**: Stellen Sie sicher, dass das Verzeichnis 'data/grafiken' existiert und beschreibbar ist
- **JSON-Ladefehler**: Falls die JSON-Datei beschädigt ist, müssen Sie sie möglicherweise löschen und neu erstellen


