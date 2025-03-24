# main.py
# Dies ist die Hauptdatei des Studiendashboard-Projekts, die alle Komponenten
# zusammenführt und die Anwendung startet. Sie enthält die Initialisierungslogik
# und die Hauptschleife für die Benutzerinteraktion.

import os
import logging
from datetime import date, timedelta

# Importe aus modularen Paketen
# Hier werden alle benötigten Klassen aus den verschiedenen Modulen importiert,
# um eine saubere und organisierte Codestruktur zu gewährleisten.
from models import Student, Studiengang, Semester, Modul, Pruefungsleistung, Note
from controllers import DatenManager, Dashboard
from views import DashboardVisualisierung, BenutzerInteraktion

# Logger konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='studiumdashboard.log'
)
logger = logging.getLogger(__name__)


def init_beispieldaten(dashboard):
    """
    Initialisiert Beispieldaten für das Dashboard zum Testen und zur Demonstration.

    Diese Funktion erstellt einen fiktiven Studenten mit mehreren abgeschlossenen und
    anstehenden Prüfungen, verschiedenen Modulen und Semestern, um die Funktionalität
    des Dashboards zu demonstrieren, ohne dass der Benutzer alle Daten manuell eingeben muss.

    Parameter:
        dashboard: Das Dashboard-Objekt, in dem die Beispieldaten gespeichert werden sollen

    Rückgabe:
        True, wenn die Beispieldaten erfolgreich erstellt wurden, sonst False
    """
    try:
        # Erstelle einen Beispielstudenten
        student = Student(
            vorname="Markus",
            nachname="Musterstudent",
            geburtsdatum=date(1985, 5, 12),
            matrikelNr="IU12079055",
            email="markus.musterstudent@iu-example.de",
            zielNotendurchschnitt=2.0,
            absolvierteECTS=0,  # Wird später berechnet
            fokus="Informatik",
            aktuelleSemesterZahl=3
        )

        # Erstelle einen Beispielstudiengang
        studiengang = Studiengang(
            name="Informatik Bachelor",
            gesamtECTS=180  # Standard für Bachelor-Studiengänge
        )

        # Erstelle Semester mit Modulen und Prüfungen
        # Wir erstellen 6 Semester für einen typischen Bachelor-Studiengang
        for i in range(1, 7):  # 6 Semester
            semester = Semester(
                nummer=i,
                # Berechne ungefähre Semesterdaten (Sommersemester Apr-Sep, Wintersemester Okt-Mär)
                startDatum=date(2022 + (i - 1) // 2, 4 if i % 2 == 1 else 10, 1),
                endDatum=date(2022 + (i - 1) // 2, 9 if i % 2 == 1 else 3, 30),
                recommendedECTS=30,
                # Setze Status basierend auf Semesterzahl des Studenten
                status="abgeschlossen" if i < 3 else ("aktiv" if i == 3 else "geplant")
            )

            # Füge Module für jedes Semester hinzu (3 Module pro Semester)
            for j in range(1, 4):
                modul = Modul(
                    modulName=f"Modul {i}.{j}",
                    modulID=f"M{i}{j}",
                    beschreibung=f"Beschreibung für Modul {i}.{j}",
                    # Verschiedene ECTS-Werte für Vielfalt
                    ects=10 if j == 1 else 5 if j == 2 else 15,
                    semesterZuordnung=i
                )

                # Füge Prüfungen für abgeschlossene Semester und aktuelles Semester hinzu
                if i < 3 or (i == 3 and j == 1):  # Nur für abgeschlossene Module Noten hinzufügen
                    pruefung = Pruefungsleistung(
                        art="Klausur" if j % 2 == 1 else "Hausarbeit",
                        # Ungefähres Datum in der Vergangenheit
                        datum=date(2022 + (i - 1) // 2, 7 if i % 2 == 1 else 2, 15),
                        beschreibung=f"Prüfung für Modul {i}.{j}"
                    )

                    # Füge Note mit verschiedenen Werten hinzu für Vielfalt
                    note = Note(
                        typ="Note",
                        # Komplexe Bedingungslogik für verschiedene Noten
                        wert=1.3 if i == 1 and j == 1 else (
                            2.0 if i == 1 and j == 2 else (
                                1.7 if i == 1 and j == 3 else (
                                    2.3 if i == 2 and j == 1 else (
                                        3.0 if i == 2 and j == 2 else (
                                            1.0 if i == 2 and j == 3 else (
                                                2.7 if i == 3 and j == 1 else 2.0
                                            )
                                        )
                                    )
                                )
                            )
                        ),
                        gewichtung=1.0
                    )

                    pruefung.set_note(note)
                    modul.add_pruefungsleistung(pruefung)
                    student.add_pruefungsleistung(pruefung)

                    # Aktualisiere ECTS, wenn bestanden
                    student.update_ects_for_modul(modul, True)

                # Füge anstehende Prüfungen für das aktuelle Semester hinzu
                if i == 3 and j > 1:
                    future_pruefung = Pruefungsleistung(
                        art="Klausur" if j % 2 == 0 else "Hausarbeit",
                        # Datum in 2 Wochen in der Zukunft
                        datum=date.today() + timedelta(days=14),
                        beschreibung=f"Anstehende Prüfung für Modul {i}.{j}"
                    )
                    modul.add_pruefungsleistung(future_pruefung)

                # Füge das Modul zum Semester hinzu
                semester.add_modul(modul)

            # Füge das Semester zum Studiengang hinzu
            studiengang.add_semester(semester)

        # Setze die Objekte im Dashboard
        dashboard.studiengang = studiengang
        dashboard.student = student

        # Speichere die Daten über den DatenManager
        return dashboard.daten_manager.speichern(studiengang, student)
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Beispieldaten: {e}", exc_info=True)
        print(f"Fehler beim Erstellen der Beispieldaten: {e}")
        return False


def main():
    """
    Hauptfunktion, die das Programm ausführt.

    Diese Funktion initialisiert alle Komponenten, lädt bestehende Daten oder erstellt
    neue (entweder Beispieldaten oder benutzerdefinierte Daten) und führt dann die
    Hauptschleife aus, in der der Benutzer mit dem Dashboard interagieren kann.
    """
    print("Initialisiere Dashboard...")
    logger.info("Anwendung gestartet")

    try:
        # Initialisiere alle Komponenten
        # Erstelle die Hauptobjekte für die Anwendung in der richtigen Reihenfolge
        daten_manager = DatenManager("data/studium_data.json")
        dashboard = Dashboard(daten_manager)
        visualisierung = DashboardVisualisierung("data/grafiken")
        benutzerinteraktion = BenutzerInteraktion(dashboard)

        # Verbinde die Komponenten miteinander
        # Dies ermöglicht die Kommunikation zwischen den verschiedenen Teilen der Anwendung
        dashboard.visualisierung = visualisierung
        dashboard.benutzerinteraktion = benutzerinteraktion

        # Versuche, bestehende Daten zu laden
        if not dashboard.initialisieren():
            print("Keine vorhandenen Daten gefunden. Erstelle neue Daten...")
            logger.info("Keine vorhandenen Daten gefunden.")

            # Frage, ob Beispieldaten verwendet werden sollen
            choice = input("Beispieldaten erstellen? (j/n): ").lower()

            if choice == 'j':
                # Erstelle Beispieldaten für schnellen Start
                if init_beispieldaten(dashboard):
                    print("Beispieldaten erfolgreich erstellt!")
                    logger.info("Beispieldaten erfolgreich erstellt.")
                else:
                    print("Fehler beim Erstellen der Beispieldaten.")
                    logger.error("Fehler beim Erstellen der Beispieldaten.")
                    return
            else:
                # Erstelle neue Daten basierend auf Benutzereingaben
                try:
                    # Führe den Benutzer durch die Erfassung von Student und Studiengang
                    student_data = benutzerinteraktion.create_new_student_data()
                    studiengang_data = benutzerinteraktion.create_new_studiengang_data()

                    # Erstelle und speichere die neuen Daten
                    if dashboard.create_new_data(student_data, studiengang_data):
                        print("Neue Daten erfolgreich erstellt!")
                        logger.info("Neue Daten erfolgreich erstellt.")
                    else:
                        print("Fehler beim Erstellen neuer Daten.")
                        logger.error("Fehler beim Erstellen neuer Daten.")
                        return
                except Exception as e:
                    print(f"Fehler bei der Eingabe: {e}")
                    logger.error(f"Fehler bei der Eingabe: {e}", exc_info=True)
                    return

        # Hauptschleife
        # Diese Schleife läuft, bis der Benutzer das Programm beendet,
        # und zeigt das Hauptmenü an, erfasst Benutzereingaben und führt die entsprechenden Aktionen aus
        running = True
        while running:
            # Zeige aktuelle Studiendaten und Hauptmenü an
            benutzerinteraktion.zeige_studiendaten()
            benutzerinteraktion.zeige_hauptmenue()

            # Erfasse und verarbeite Benutzereingabe
            choice = input("\nAuswahl treffen (0-9): ")

            # Eingabevalidierung
            try:
                choice_num = int(choice)
                if choice_num < 0 or choice_num > 9:
                    print("Ungültige Auswahl. Bitte eine Zahl zwischen 0 und 9 eingeben.")
                    continue

                # Führe die entsprechende Aktion basierend auf der Benutzereingabe aus
                if choice_num == 0:
                    running = False  # Beende die Schleife und das Programm
                    logger.info("Anwendung wird beendet.")
                elif choice_num == 1:
                    benutzerinteraktion.zeige_notendurchschnitt()  # Zeige Notendurchschnitt an
                elif choice_num == 2:
                    benutzerinteraktion.zeige_ects_fortschritt()  # Zeige ECTS-Fortschritt an
                elif choice_num == 3:
                    benutzerinteraktion.zeige_notenverteilung()  # Zeige Notenverteilung an
                    benutzerinteraktion.erstelle_grafiken()  # Erstelle optional Grafiken
                elif choice_num == 4:
                    benutzerinteraktion.zeige_anstehende_pruefungen()  # Zeige anstehende Prüfungen an
                elif choice_num == 5:
                    benutzerinteraktion.erfasse_note()  # Erfasse eine neue Note
                elif choice_num == 6:
                    benutzerinteraktion.erfasse_modul()  # Erfasse ein neues Modul
                elif choice_num == 7:
                    benutzerinteraktion.bearbeite_ziele()  # Bearbeite Ziel-Notendurchschnitt
                elif choice_num == 8:
                    benutzerinteraktion.exportiere_daten()  # Exportiere Daten
                elif choice_num == 9:
                    benutzerinteraktion.importiere_daten()  # Importiere Daten
            except ValueError:
                print("Ungültige Eingabe. Bitte eine Zahl eingeben.")

        print("Programm wird beendet. Auf Wiedersehen!")
    except Exception as e:
        logger.critical(f"Unerwarteter Fehler in der Hauptfunktion: {e}", exc_info=True)
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        print("Details wurden in die Log-Datei geschrieben.")


if __name__ == "__main__":
    # Dieser Block wird nur ausgeführt, wenn die Datei direkt gestartet wird
    # und nicht, wenn sie als Modul importiert wird

    # Stelle sicher, dass die benötigten Verzeichnisse existieren
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/grafiken", exist_ok=True)

    # Führe die Hauptfunktion aus
    main()