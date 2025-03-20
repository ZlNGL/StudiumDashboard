# controllers/datenmanager.py
import json
import os
import csv
import logging
from datetime import date
from typing import List, Dict, Optional, Tuple, Set, Union, Any

# Importe für Modellklassen
from models import Student, Studiengang, Semester, Modul, Pruefungsleistung, Note

# Logger konfigurieren
logger = logging.getLogger(__name__)


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
            logger.error(f"Fehler beim Speichern: {e}", exc_info=True)
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
                logger.info(f"Datei nicht gefunden: {self.datei_pfad}")
                print(f"Datei nicht gefunden: {self.datei_pfad}")
                return None, None

            # Lese die JSON-Datei
            with open(self.datei_pfad, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Überprüfe, ob die erwarteten Schlüssel vorhanden sind
            if "studiengang" not in data or "student" not in data:
                logger.error(f"Ungültiges Dateiformat: Erforderliche Schlüssel fehlen")
                print(f"Ungültiges Dateiformat: Erforderliche Schlüssel fehlen")
                return None, None

            # Konvertiere die geladenen Daten zurück in Objekte
            studiengang = Studiengang.from_dict(data["studiengang"])
            student = Student.from_dict(data["student"])

            return studiengang, student
        except json.JSONDecodeError as e:
            logger.error(f"Fehler beim Parsen der JSON-Datei: {e}", exc_info=True)
            print(f"Fehler beim Parsen der JSON-Datei: {e}")
            return None, None
        except Exception as e:
            logger.error(f"Fehler beim Laden: {e}", exc_info=True)
            print(f"Fehler beim Laden: {e}")
            return None, None

    def export_csv(self, student: Student, studiengang: Studiengang, export_pfad: str = "noten_export.csv") -> bool:
        """
        Exportiert Studentennoten in eine CSV-Datei.

        Diese Methode generiert eine strukturierte CSV-Datei mit allen Prüfungsleistungen
        des Studenten, was den Export in andere Anwendungen oder zur Archivierung ermöglicht.
        Die Methode wurde erweitert, um auch Modulinformationen zu exportieren.

        Parameter:
            student: Das Student-Objekt, dessen Noten exportiert werden sollen
            studiengang: Das Studiengang-Objekt für Modulinformationen
            export_pfad: Pfad zur Export-Datei (Standard: "noten_export.csv")

        Rückgabe:
            True, wenn der Export erfolgreich war, False sonst
        """
        try:
            if not student:
                raise ValueError("Student muss angegeben werden")

            pruefungen = student.get_pruefungsleistungen()
            module = {modul.id: modul for modul in studiengang.get_all_module()}

            # Erstelle das Verzeichnis, falls es nicht existiert
            directory = os.path.dirname(export_pfad)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            # Erstelle die CSV-Datei und schreibe die Daten
            with open(export_pfad, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)

                # Erweiterte Kopfzeile mit Modulinformationen
                writer.writerow([
                    "Modul_ID", "Modul_Name", "Prüfungsart", "Datum", "Beschreibung",
                    "Note", "Gewichtung", "Bestanden"
                ])

                # Schreibe die Daten für jede Prüfungsleistung
                for pruefung in pruefungen:
                    note_wert = pruefung.note.wert if pruefung.note else "N/A"
                    gewichtung = pruefung.note.gewichtung if pruefung.note else 1.0

                    # Finde das zugehörige Modul
                    modul_id = pruefung.modul_id
                    modul_name = "Unbekannt"
                    if modul_id and modul_id in module:
                        modul_name = module[modul_id].modulName

                    writer.writerow([
                        modul_id or "",
                        modul_name,
                        pruefung.art,
                        pruefung.datum.isoformat() if pruefung.datum else "N/A",
                        pruefung.beschreibung,
                        note_wert,
                        gewichtung,
                        "Ja" if pruefung.bestanden else "Nein"
                    ])

            return True
        except Exception as e:
            logger.error(f"Fehler beim CSV-Export: {e}", exc_info=True)
            print(f"Fehler beim CSV-Export: {e}")
            return False

    def import_csv(self, student: Student, studiengang: Studiengang, import_pfad: str) -> bool:
        """
        Importiert Noten aus einer CSV-Datei.

        Diese Methode liest eine CSV-Datei mit Prüfungsdaten und fügt die
        entsprechenden Prüfungsleistungen zum Studenten und zu den passenden
        Modulen des Studiengangs hinzu. Die Methode wurde verbessert, um Modul-IDs
        für eine bessere Zuordnung zu verwenden.

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
                logger.error(f"Import-Datei nicht gefunden: {import_pfad}")
                print(f"Import-Datei nicht gefunden: {import_pfad}")
                return False

            # Sammle alle Module für schnelleren Zugriff
            module_by_id = {modul.id: modul for modul in studiengang.get_all_module()}
            module_by_name = {modul.modulName: modul for modul in studiengang.get_all_module()}

            # Überprüfe die CSV-Struktur
            with open(import_pfad, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader, None)
                # Überprüfe grundlegende Spalten
                if not header or not any(col in header for col in ["Prüfungsart", "Note"]):
                    logger.error(f"CSV-Datei hat nicht das erwartete Format.")
                    print(f"CSV-Datei hat nicht das erwartete Format.")
                    return False

            # Lese die CSV-Datei
            with open(import_pfad, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                # Verarbeite jede Zeile der CSV-Datei
                for row in reader:
                    try:
                        # Ermittle das Modul (entweder über ID oder Name)
                        modul = None
                        modul_id = row.get("Modul_ID")
                        modul_name = row.get("Modul_Name")

                        if modul_id and modul_id in module_by_id:
                            modul = module_by_id[modul_id]
                        elif modul_name and modul_name in module_by_name:
                            modul = module_by_name[modul_name]
                        elif modul_name:
                            # Wenn das Modul nicht existiert, erstelle ein neues
                            logger.info(f"Modul '{modul_name}' nicht gefunden. Erstelle neu.")
                            print(f"Modul '{modul_name}' nicht gefunden. Erstelle neu.")
                            modul = Modul(
                                modulName=modul_name,
                                modulID=f"M{len(module_by_name) + 1}",
                                ects=5,  # Standardwert
                                semesterZuordnung=1  # Standardwert
                            )
                            # Füge zum ersten Semester hinzu oder erstelle ein Semester
                            semester = studiengang.get_semester(1)
                            if not semester:
                                semester = Semester(nummer=1)
                                studiengang.add_semester(semester)
                            semester.add_modul(modul)

                            # Aktualisiere Lookup-Dictionaries
                            module_by_id[modul.id] = modul
                            module_by_name[modul.modulName] = modul

                        # Erstelle eine neue Prüfungsleistung
                        pruefung = Pruefungsleistung(
                            art=row.get("Prüfungsart", "Unbekannt"),
                            datum=date.fromisoformat(row.get("Datum")) if row.get("Datum") and row.get(
                                "Datum") != "N/A" else date.today(),
                            beschreibung=row.get("Beschreibung", "")
                        )

                        # Setze die Modul-ID, falls ein Modul gefunden wurde
                        if modul:
                            pruefung.modul_id = modul.id

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
                                logger.warning(f"Ungültiger Notenwert: {note_wert}. Überspringe Note.")
                                print(f"Ungültiger Notenwert: {note_wert}. Überspringe Note.")
                                continue

                        # Füge zum Studenten hinzu
                        student.add_pruefungsleistung(pruefung)

                        # Füge zum Modul hinzu, falls gefunden
                        if modul:
                            modul.add_pruefungsleistung(pruefung)
                            # Aktualisiere ECTS-Status, falls die Prüfung bestanden ist
                            if pruefung.bestanden:
                                student.update_ects_for_modul(modul, True)

                    except Exception as e:
                        logger.error(f"Fehler beim Importieren einer Zeile: {e}", exc_info=True)
                        print(f"Fehler beim Importieren einer Zeile: {e}")
                        continue  # Fahre mit der nächsten Zeile fort, auch wenn diese fehlschlägt

            return True
        except Exception as e:
            logger.error(f"Fehler beim CSV-Import: {e}", exc_info=True)
            print(f"Fehler beim CSV-Import: {e}")
            return False