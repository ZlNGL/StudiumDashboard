# controllers/datenmanager.py
import json
import os
import csv
from datetime import date
from typing import List, Dict, Optional, Tuple, Set, Union, Any

# Importe für Modellklassen
from models import Student, Studiengang, Semester, Modul, Pruefungsleistung, Note


class DatenManager:
    """
    Klasse, die für Datenverwaltungsoperationen wie das Speichern, Laden,
    Importieren und Exportieren von Daten verantwortlich ist.

    Der DatenManager dient als zentrale Komponente für die Persistenz von
    Daten und bietet eine einheitliche Schnittstelle für den Zugriff auf
    verschiedene Dateiformate (JSON, CSV).
    """

    def __init__(self, datei_pfad: str = "data.json"):
        """
        Initialisiert ein DatenManager-Objekt mit dem angegebenen Dateipfad.

        Parameter:
            datei_pfad: Pfad zur Datendatei (Standard: "data.json")
        """
        self.datei_pfad = datei_pfad

    def speichern(self, studiengang: Studiengang, student: Student) -> bool:
        """
        Speichert den aktuellen Zustand des Studiengangs und des Studenten in eine Datei.

        Diese Methode konvertiert die Objekte in serialisierbare Dictionaries und
        speichert sie als JSON-Datei. Sie erstellt auch das Verzeichnis, falls es nicht existiert.

        Parameter:
            studiengang: Das zu speichernde Studiengang-Objekt
            student: Das zu speichernde Student-Objekt

        Rückgabe:
            True, wenn der Speichervorgang erfolgreich war, False sonst
        """
        try:
            # Stelle sicher, dass beide Objekte existieren
            if not studiengang or not student:
                raise ValueError("Studiengang und Student müssen angegeben werden")

            # Erstelle ein Dictionary mit den zu speichernden Daten
            data = {
                "studiengang": studiengang.to_dict(),
                "student": student.to_dict()
            }

            # Stelle sicher, dass das Verzeichnis existiert
            directory = os.path.dirname(self.datei_pfad)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            # Schreibe die Daten in die JSON-Datei
            with open(self.datei_pfad, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)  # Unicode-Zeichen und Einrückung für Lesbarkeit
            return True
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
            return False

    def laden(self) -> Tuple[Optional[Studiengang], Optional[Student]]:
        """
        Lädt Studiengang- und Studentendaten aus einer Datei.

        Diese Methode liest die JSON-Datei und konvertiert die Daten zurück
        in Studiengang- und Student-Objekte.

        Rückgabe:
            Ein Tupel mit den geladenen Studiengang- und Student-Objekten,
            oder (None, None), wenn das Laden fehlgeschlagen ist
        """
        try:
            # Überprüfe, ob die Datei existiert
            if not os.path.exists(self.datei_pfad):
                print(f"Datei nicht gefunden: {self.datei_pfad}")
                return None, None

            # Lese die JSON-Datei
            with open(self.datei_pfad, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Überprüfe, ob die erwarteten Schlüssel vorhanden sind
            if "studiengang" not in data or "student" not in data:
                print(f"Ungültiges Dateiformat: Erforderliche Schlüssel fehlen")
                return None, None

            # Konvertiere die geladenen Daten zurück in Objekte
            studiengang = Studiengang.from_dict(data["studiengang"])
            student = Student.from_dict(data["student"])

            return studiengang, student
        except json.JSONDecodeError as e:
            print(f"Fehler beim Parsen der JSON-Datei: {e}")
            return None, None
        except Exception as e:
            print(f"Fehler beim Laden: {e}")
            return None, None

    def export_csv(self, student: Student, export_pfad: str = "noten_export.csv") -> bool:
        """
        Exportiert Studentennoten in eine CSV-Datei.

        Diese Methode generiert eine strukturierte CSV-Datei mit allen Prüfungsleistungen
        des Studenten, was den Export in andere Anwendungen oder zur Archivierung ermöglicht.

        Parameter:
            student: Das Student-Objekt, dessen Noten exportiert werden sollen
            export_pfad: Pfad zur Export-Datei (Standard: "noten_export.csv")

        Rückgabe:
            True, wenn der Export erfolgreich war, False sonst
        """
        try:
            if not student:
                raise ValueError("Student muss angegeben werden")

            pruefungen = student.get_pruefungsleistungen()

            # Erstelle das Verzeichnis, falls es nicht existiert
            directory = os.path.dirname(export_pfad)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            # Erstelle die CSV-Datei und schreibe die Daten
            with open(export_pfad, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)

                # Schreibe die Kopfzeile
                writer.writerow([
                    "Prüfungsart", "Datum", "Beschreibung",
                    "Note", "Gewichtung", "Bestanden"
                ])

                # Schreibe die Daten für jede Prüfungsleistung
                for pruefung in pruefungen:
                    note_wert = pruefung.note.wert if pruefung.note else "N/A"
                    gewichtung = pruefung.note.gewichtung if pruefung.note else 1.0

                    writer.writerow([
                        pruefung.art,
                        pruefung.datum.isoformat() if pruefung.datum else "N/A",
                        pruefung.beschreibung,
                        note_wert,
                        gewichtung,
                        "Ja" if pruefung.bestanden else "Nein"
                    ])

            return True
        except Exception as e:
            print(f"Fehler beim CSV-Export: {e}")
            return False

    def import_csv(self, student: Student, studiengang: Studiengang, import_pfad: str) -> bool:
        """
        Importiert Noten aus einer CSV-Datei.

        Diese Methode liest eine CSV-Datei mit Prüfungsdaten und fügt die
        entsprechenden Prüfungsleistungen zum Studenten und zu den passenden
        Modulen des Studiengangs hinzu.

        Parameter:
            student: Das Student-Objekt, zu dem die Noten hinzugefügt werden sollen
            studiengang: Das Studiengang-Objekt, das die Module enthält
            import_pfad: Pfad zur Import-Datei

        Rückgabe:
            True, wenn der Import erfolgreich war, False sonst
        """
        try:
            # Überprüfe, ob die Datei existiert
            if not os.path.exists(import_pfad):
                print(f"Import-Datei nicht gefunden: {import_pfad}")
                return False

            # Überprüfe die CSV-Struktur
            required_columns = ["Prüfungsart", "Datum", "Beschreibung", "Note", "Gewichtung", "Bestanden"]
            with open(import_pfad, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader, None)
                if not header or not all(col in header for col in required_columns):
                    print(f"CSV-Datei hat nicht das erwartete Format. Benötigte Spalten: {required_columns}")
                    return False

            # Lese die CSV-Datei
            with open(import_pfad, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                # Verarbeite jede Zeile der CSV-Datei
                for row in reader:
                    try:
                        # Erstelle eine neue Prüfungsleistung
                        pruefung = Pruefungsleistung(
                            art=row.get("Prüfungsart", "Unbekannt"),
                            datum=date.fromisoformat(row.get("Datum")) if row.get("Datum") and row.get(
                                "Datum") != "N/A" else None,
                            beschreibung=row.get("Beschreibung", "")
                        )

                        # Füge Note hinzu, falls vorhanden
                        note_wert = row.get("Note")
                        if note_wert and note_wert != "N/A":
                            try:
                                note_wert_float = float(note_wert)
                                gewichtung = float(row.get("Gewichtung", 1.0))
                                note = Note(
                                    typ=row.get("Prüfungsart", "Unbekannt"),
                                    wert=note_wert_float,
                                    gewichtung=gewichtung
                                )
                                pruefung.set_note(note)
                            except ValueError:
                                print(f"Ungültiger Notenwert: {note_wert}. Überspringe Note.")
                                continue

                        # Füge zum Studenten hinzu
                        student.add_pruefungsleistung(pruefung)

                        # Finde das entsprechende Modul und aktualisiere es
                        # In einer vollständigen Implementierung würde man einen zuverlässigeren
                        # Weg verwenden, um Prüfungen mit Modulen zu verknüpfen (z.B. über Modul-IDs)
                        if row.get("Modul"):
                            for modul in studiengang.get_all_module():
                                if modul.modulName == row.get("Modul"):
                                    modul.add_pruefungsleistung(pruefung)
                                    break

                    except Exception as e:
                        print(f"Fehler beim Importieren einer Zeile: {e}")
                        continue  # Fahre mit der nächsten Zeile fort, auch wenn diese fehlschlägt

            return True
        except Exception as e:
            print(f"Fehler beim CSV-Import: {e}")
            return False