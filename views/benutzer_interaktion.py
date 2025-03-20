# views/benutzer_interaktion.py
from datetime import date
from typing import Dict, Any, Optional
import traceback
import logging

# Logger konfigurieren
logger = logging.getLogger(__name__)


class BenutzerInteraktion:
    """
    Klasse für die Benutzerinteraktion, z.B. Anzeige des Hauptmenüs und
    Erfassung von Eingaben.

    Diese Klasse ist die Schnittstelle zwischen dem Benutzer und dem System.
    Sie zeigt Menüs und Informationen an, erfasst Benutzereingaben und leitet
    diese an die entsprechenden Controller-Methoden weiter.
    """

    def __init__(self, dashboard=None):
        """
        Initialisiert ein BenutzerInteraktion-Objekt mit dem angegebenen Dashboard.

        Parameter:
            dashboard: Das Dashboard-Objekt, mit dem interagiert werden soll (optional)
        """
        self.dashboard = dashboard

    def get_validated_date(self, prompt="Datum (TT.MM.JJJJ): ", allow_empty=True):
        """
        Fragt den Benutzer nach einem Datum und validiert die Eingabe.

        Parameter:
            prompt: Die Eingabeaufforderung
            allow_empty: Ob eine leere Eingabe erlaubt ist

        Rückgabe:
            Ein date-Objekt oder None, wenn allow_empty True ist und keine Eingabe erfolgte
        """
        while True:
            datum_str = input(prompt)
            if not datum_str and allow_empty:
                return None

            try:
                if "." in datum_str:  # Deutsches Format: TT.MM.JJJJ
                    tag, monat, jahr = map(int, datum_str.split('.'))
                    return date(jahr, monat, tag)
                elif "-" in datum_str:  # ISO-Format: JJJJ-MM-TT
                    return date.fromisoformat(datum_str)
                else:
                    print("Ungültiges Datumsformat. Bitte als TT.MM.JJJJ oder JJJJ-MM-TT eingeben.")
            except ValueError as e:
                print(f"Ungültiges Datum: {e}")

    def zeige_hauptmenue(self) -> None:
        """
        Zeigt das Hauptmenü an.

        Diese Methode gibt das Hauptmenü mit allen verfügbaren Optionen auf der
        Konsole aus. Der Benutzer kann dann eine Option wählen.
        """
        print("\n" + "=" * 50)
        print("MEIN STUDIUM DASHBOARD")
        print("=" * 50)
        print("1. Notendurchschnitt anzeigen")
        print("2. ECTS-Fortschritt anzeigen")
        print("3. Notenverteilung anzeigen")
        print("4. Anstehende Prüfungen anzeigen")
        print("5. Note erfassen")
        print("6. Modul erfassen")
        print("7. Ziel-Notendurchschnitt bearbeiten")
        print("8. Daten exportieren")
        print("9. Daten importieren")
        print("0. Beenden")
        print("=" * 50)

    def zeige_studiendaten(self) -> None:
        """
        Zeigt allgemeine Studiendaten an.

        Diese Methode gibt einen Überblick über die wichtigsten Studiendaten wie
        Studiengang, Student, Semester, ECTS-Fortschritt und Notendurchschnitt aus.
        """
        if not self.dashboard or not (self.dashboard.studiengang and self.dashboard.student):
            print("Keine Studiendaten verfügbar.")
            return

        studiengang = self.dashboard.studiengang
        student = self.dashboard.student

        print("\n" + "=" * 50)
        print(f"Studiengang: {studiengang.name}")
        print(f"Student: {student.get_fullname()} (Matrikel-Nr: {student.matrikelNr})")
        print(f"Aktuelles Semester: {student.aktuelleSemesterZahl}")

        # Berechne ECTS-Fortschritt sicher
        ects_prozent = 0
        if studiengang.gesamtECTS > 0:
            ects_prozent = (student.absolvierteECTS / studiengang.gesamtECTS * 100)

        print(f"ECTS-Fortschritt: {student.absolvierteECTS}/{studiengang.gesamtECTS} ({ects_prozent:.1f}%)")
        print(f"Aktueller Notendurchschnitt: {student.get_durchschnittnote():.2f}")
        print(f"Ziel-Notendurchschnitt: {student.zielNotendurchschnitt:.2f}")
        print("=" * 50)

    def zeige_notendurchschnitt(self) -> None:
        """
        Zeigt den Notendurchschnitt an.

        Diese Methode gibt detaillierte Informationen zum aktuellen Notendurchschnitt
        und dem Zielwert aus, inklusive einer Statusmeldung zur Zielerreichung.
        """
        if not self.dashboard:
            print("Dashboard nicht initialisiert.")
            return

        durchschnitt = self.dashboard.berechne_notendurchschnitt()
        ziel = self.dashboard.student.zielNotendurchschnitt if self.dashboard.student else 2.0

        print("\n" + "=" * 50)
        print("NOTENDURCHSCHNITT")
        print("=" * 50)
        print(f"Aktueller Notendurchschnitt: {durchschnitt:.2f}")
        print(f"Ziel-Notendurchschnitt: {ziel:.2f}")

        # Zeige Status der Zielerreichung an
        if durchschnitt <= ziel:
            print("Status: Ziel erreicht! ✅")
        else:
            print(f"Status: Noch {durchschnitt - ziel:.2f} Punkte vom Ziel entfernt")

        print("=" * 50)

    def zeige_ects_fortschritt(self) -> None:
        """
        Zeigt den ECTS-Fortschritt an.

        Diese Methode gibt detaillierte Informationen zum aktuellen ECTS-Fortschritt aus,
        darunter absolvierte und gesamte ECTS sowie den prozentualen Fortschritt.
        """
        if not self.dashboard:
            print("Dashboard nicht initialisiert.")
            return

        fortschritt = self.dashboard.berechne_ects_fortschritt()

        print("\n" + "=" * 50)
        print("ECTS-FORTSCHRITT")
        print("=" * 50)
        print(f"Absolvierte ECTS: {fortschritt['absolut']}")
        print(f"Gesamte ECTS: {fortschritt['gesamt']}")
        print(f"Fortschritt: {fortschritt['prozent']:.1f}%")
        print(f"Noch benötigte ECTS: {fortschritt['gesamt'] - fortschritt['absolut']}")
        print("=" * 50)

    def zeige_notenverteilung(self) -> None:
        """
        Zeigt die Notenverteilung an.

        Diese Methode gibt eine tabellarische Übersicht über die Häufigkeit
        der verschiedenen Noten aus, sortiert nach Notenwert.
        """
        if not self.dashboard:
            print("Dashboard nicht initialisiert.")
            return

        verteilung = self.dashboard.zeige_notenverteilung()

        print("\n" + "=" * 50)
        print("NOTENVERTEILUNG")
        print("=" * 50)

        if not verteilung:
            print("Keine Noten vorhanden.")
        else:
            # Sortiere Noten aufsteigend für bessere Lesbarkeit
            sorted_keys = sorted(verteilung.keys(), key=lambda x: float(x))
            for note in sorted_keys:
                count = verteilung[note]
                print(f"Note {note}: {count}x")

        print("=" * 50)

    def zeige_anstehende_pruefungen(self) -> None:
        """
        Zeigt anstehende Prüfungen an.

        Diese Methode gibt eine Liste der anstehenden Prüfungen innerhalb der
        nächsten 30 Tage aus, sortiert nach Datum.
        """
        if not self.dashboard:
            print("Dashboard nicht initialisiert.")
            return

        upcoming = self.dashboard.anstehende_pruefungen()

        print("\n" + "=" * 50)
        print("ANSTEHENDE PRÜFUNGEN")
        print("=" * 50)

        if not upcoming:
            print("Keine anstehenden Prüfungen in den nächsten 30 Tagen.")
        else:
            for i, pruefung in enumerate(upcoming, 1):
                # Formatiere das Datum für bessere Lesbarkeit
                datum_str = pruefung.datum.strftime("%d.%m.%Y") if pruefung.datum else "Kein Datum"
                print(f"{i}. {pruefung.art}: {pruefung.beschreibung} (Datum: {datum_str})")

        print("=" * 50)

    def erfasse_note(self) -> None:
        """
        Erfasst eine neue Note.

        Diese Methode führt den Benutzer durch den Prozess der Erfassung einer
        neuen Note für ein Modul, mit Eingabeaufforderungen für alle relevanten Daten.
        """
        if not self.dashboard or not self.dashboard.studiengang:
            print("Dashboard oder Studiengang nicht initialisiert.")
            return

        print("\n" + "=" * 50)
        print("NOTE ERFASSEN")
        print("=" * 50)

        # Zeige verfügbare Module an
        alle_module = self.dashboard.studiengang.get_all_module()
        if not alle_module:
            print("Keine Module vorhanden. Bitte erst ein Modul erfassen.")
            return

        print("Verfügbare Module:")
        for i, modul in enumerate(alle_module, 1):
            print(f"{i}. {modul.modulName} ({modul.ects} ECTS)")

        try:
            # Wähle Modul aus
            modul_index = int(input("\nModul-Nummer auswählen: ")) - 1
            if modul_index < 0 or modul_index >= len(alle_module):
                print("Ungültige Auswahl.")
                return

            modul = alle_module[modul_index]

            # Erfasse Prüfungsdaten
            pruefung_data = {}
            pruefung_data["art"] = input("Prüfungsart (Klausur, Hausarbeit, etc.): ")

            # Verbesserte Datumseingabe mit Validierung
            pruefung_data["datum"] = self.get_validated_date("Datum (TT.MM.JJJJ, leer für heute): ")
            if not pruefung_data["datum"]:
                pruefung_data["datum"] = date.today()

            pruefung_data["beschreibung"] = input("Beschreibung: ")
            pruefung_data["typ"] = input("Notentyp (Klausur, Hausarbeit, etc.): ")

            # Erfasse Note mit Fehlerbehandlung
            while True:
                wert_str = input("Note (z.B. 1.7): ")
                try:
                    pruefung_data["wert"] = float(wert_str.replace(',', '.'))
                    break
                except ValueError:
                    print("Ungültiger Notenwert. Bitte eine Zahl eingeben.")

            # Erfasse optionale Gewichtung mit Fehlerbehandlung
            while True:
                gewichtung_str = input("Gewichtung (1.0 für normal, leer für Standard): ")
                if not gewichtung_str:
                    pruefung_data["gewichtung"] = 1.0
                    break
                try:
                    pruefung_data["gewichtung"] = float(gewichtung_str.replace(',', '.'))
                    break
                except ValueError:
                    print("Ungültige Gewichtung. Bitte eine Zahl eingeben oder leer lassen.")

            # Speichere die Note
            if self.dashboard.erfasse_note(modul.modulName, pruefung_data):
                print("Note erfolgreich erfasst.")
            else:
                print("Fehler beim Erfassen der Note.")
        except Exception as e:
            logger.error(f"Fehler bei der Noteneingabe: {e}", exc_info=True)
            print(f"Fehler bei der Eingabe: {e}")

    def erfasse_modul(self) -> None:
        """
        Erfasst ein neues Modul.

        Diese Methode führt den Benutzer durch den Prozess der Erfassung eines
        neuen Moduls, mit Eingabeaufforderungen für alle relevanten Daten.
        """
        if not self.dashboard:
            print("Dashboard nicht initialisiert.")
            return

        print("\n" + "=" * 50)
        print("MODUL ERFASSEN")
        print("=" * 50)

        try:
            # Erfasse Moduldaten
            modul_data = {}
            modul_data["name"] = input("Modulname: ")
            modul_data["id"] = input("Modul-ID (leer für automatisch): ")
            modul_data["beschreibung"] = input("Beschreibung: ")

            # Erfasse ECTS-Punkte mit Fehlerbehandlung
            while True:
                ects_str = input("ECTS (Standard: 5): ")
                if not ects_str:
                    modul_data["ects"] = 5
                    break
                try:
                    modul_data["ects"] = int(ects_str)
                    break
                except ValueError:
                    print("Ungültige ECTS-Punktzahl. Bitte eine ganze Zahl eingeben oder leer lassen.")

            # Erfasse Semester mit Fehlerbehandlung
            while True:
                semester_str = input("Semester (1, 2, etc.): ")
                if not semester_str:
                    semester = 1
                    break
                try:
                    semester = int(semester_str)
                    break
                except ValueError:
                    print("Ungültige Semesterzahl. Bitte eine ganze Zahl eingeben oder leer lassen.")

            # Speichere das Modul
            if self.dashboard.erfasse_modul(semester, modul_data):
                print("Modul erfolgreich erfasst.")
            else:
                print("Fehler beim Erfassen des Moduls.")
        except Exception as e:
            logger.error(f"Fehler bei der Moduleingabe: {e}", exc_info=True)
            print(f"Fehler bei der Eingabe: {e}")

    def bearbeite_ziele(self) -> None:
        """
        Aktualisiert den Ziel-Notendurchschnitt.

        Diese Methode ermöglicht es dem Benutzer, seinen angestrebten
        Notendurchschnitt zu ändern und zu speichern.
        """
        if not self.dashboard or not self.dashboard.student:
            print("Dashboard oder Student nicht initialisiert.")
            return

        print("\n" + "=" * 50)
        print("ZIEL-NOTENDURCHSCHNITT BEARBEITEN")
        print("=" * 50)

        # Zeige aktuellen Zielwert
        current = self.dashboard.student.zielNotendurchschnitt
        print(f"Aktueller Ziel-Notendurchschnitt: {current:.2f}")

        try:
            # Erfasse neuen Zielwert mit Fehlerbehandlung
            while True:
                ziel_str = input("Neuer Ziel-Notendurchschnitt: ")
                try:
                    ziel = float(ziel_str.replace(',', '.'))  # Erlaube Eingabe mit Komma oder Punkt
                    break
                except ValueError:
                    print("Ungültiger Notenwert. Bitte eine Zahl eingeben.")

            # Speichere den neuen Zielwert
            if self.dashboard.bearbeite_ziele(ziel):
                print("Ziel erfolgreich aktualisiert.")
            else:
                print("Fehler beim Aktualisieren des Ziels.")
        except Exception as e:
            logger.error(f"Fehler bei der Zielbearbeitung: {e}", exc_info=True)
            print(f"Fehler bei der Eingabe: {e}")

    def exportiere_daten(self) -> None:
        """
        Exportiert Daten in eine CSV-Datei.

        Diese Methode ermöglicht es dem Benutzer, seine Notendaten
        in eine CSV-Datei zu exportieren.
        """
        if not self.dashboard:
            print("Dashboard nicht initialisiert.")
            return

        print("\n" + "=" * 50)
        print("DATEN EXPORTIEREN")
        print("=" * 50)

        # Erfasse Exportpfad
        export_pfad = input("Exportpfad (Standard: noten_export.csv): ")
        export_pfad = export_pfad if export_pfad else "noten_export.csv"

        # Führe Export durch
        if self.dashboard.exportiere_daten(export_pfad):
            print(f"Daten erfolgreich nach '{export_pfad}' exportiert.")
        else:
            print("Fehler beim Exportieren der Daten.")

    def importiere_daten(self) -> None:
        """
        Importiert Daten aus einer CSV-Datei.

        Diese Methode ermöglicht es dem Benutzer, Notendaten aus einer
        CSV-Datei zu importieren und zum bestehenden Datensatz hinzuzufügen.
        """
        if not self.dashboard:
            print("Dashboard nicht initialisiert.")
            return

        print("\n" + "=" * 50)
        print("DATEN IMPORTIEREN")
        print("=" * 50)

        # Erfasse Importpfad
        import_pfad = input("Importpfad: ")

        if not import_pfad:
            print("Kein Pfad angegeben.")
            return

        # Führe Import durch
        if self.dashboard.importiere_daten(import_pfad):
            print(f"Daten erfolgreich von '{import_pfad}' importiert.")
        else:
            print("Fehler beim Importieren der Daten.")

    def erstelle_grafiken(self) -> None:
        """
        Erstellt Visualisierungen der Studiendaten.

        Diese Methode nutzt die DashboardVisualisierung-Klasse, um verschiedene
        Grafiken wie ECTS-Fortschritt, Notenübersicht und Semesterdurchschnitte
        zu generieren und zu speichern.
        """
        if not self.dashboard or not hasattr(self.dashboard, 'visualisierung') or not self.dashboard.visualisierung:
            print("Dashboard oder Visualisierung nicht initialisiert.")
            return

        print("\n" + "=" * 50)
        print("GRAFIKEN ERSTELLEN")
        print("=" * 50)

        try:
            # Nutze die Visualisierungsklasse für die Grafikerstellung
            vis = self.dashboard.visualisierung

            # ECTS-Fortschritt visualisieren
            fortschritt = self.dashboard.berechne_ects_fortschritt()
            if fortschritt and 'absolut' in fortschritt and 'gesamt' in fortschritt:
                ects_pfad = vis.erstelle_fortschrittsbalken(
                    float(fortschritt['absolut']),
                    float(fortschritt['gesamt']),
                    "ECTS-Fortschritt",
                    "ects_fortschritt"
                )
                print(f"Grafik für ECTS-Fortschritt erstellt: {ects_pfad}")
            else:
                print("Keine ECTS-Fortschrittsdaten verfügbar.")

            # Notendurchschnitt und -verteilung visualisieren
            durchschnitt = self.dashboard.berechne_notendurchschnitt()
            ziel = 2.0  # Standardwert
            if self.dashboard.student and hasattr(self.dashboard.student, 'zielNotendurchschnitt'):
                ziel = self.dashboard.student.zielNotendurchschnitt

            noten_data = {
                "aktuell": float(durchschnitt) if durchschnitt else 0.0,
                "verteilung": self.dashboard.zeige_notenverteilung() or {}
            }

            noten_pfad = vis.erstelle_notenuebersicht(
                noten_data,
                float(ziel),
                "notenuebersicht"
            )
            print(f"Grafik für Notenübersicht erstellt: {noten_pfad}")

            # Semesterdurchschnitte visualisieren
            semester_noten = self.dashboard.zeige_semesterdurchschnitte() or {}
            if semester_noten:
                # Konvertiere alle Schlüssel zu Strings für matplotlib
                semester_noten_str = {str(k): float(v) for k, v in semester_noten.items()}
                if semester_noten_str:
                    semester_pfad = vis.erstelle_liniendiagramm(
                        semester_noten_str,
                        "Notendurchschnitt pro Semester",
                        "Semester",
                        "Notendurchschnitt",
                        "semesterdurchschnitte"
                    )
                    print(f"Grafik für Semesterdurchschnitte erstellt: {semester_pfad}")
                else:
                    print("Keine ausreichenden Semesterdaten für Diagramm verfügbar.")
            else:
                print("Keine Semesterdurchschnittsdaten verfügbar.")

        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Grafiken: {e}", exc_info=True)
            print(f"Fehler beim Erstellen der Grafiken: {e}")

    def create_new_student_data(self) -> Dict[str, Any]:
        """
        Erstellt neue Studentendaten basierend auf Benutzereingaben.

        Diese Methode führt den Benutzer durch den Prozess der Erfassung
        aller notwendigen Informationen für einen neuen Studenten.

        Rückgabe:
            Dictionary mit Studenteninformationen
        """
        print("\n" + "=" * 50)
        print("NEUEN STUDENTEN ERSTELLEN")
        print("=" * 50)

        student_data = {}
        student_data["vorname"] = input("Vorname: ")
        student_data["nachname"] = input("Nachname: ")

        # Verbesserte Datumseingabe mit Validierung
        student_data["geburtsdatum"] = self.get_validated_date("Geburtsdatum (TT.MM.JJJJ, leer für heute): ")
        if not student_data["geburtsdatum"]:
            student_data["geburtsdatum"] = date.today()

        student_data["matrikelNr"] = input("Matrikel-Nr: ")
        student_data["email"] = input("E-Mail: ")

        # Erfasse Ziel-Notendurchschnitt mit Fehlerbehandlung
        while True:
            ziel_str = input("Ziel-Notendurchschnitt (Standard: 2.0): ")
            if not ziel_str:
                student_data["zielNotendurchschnitt"] = 2.0
                break
            try:
                student_data["zielNotendurchschnitt"] = float(ziel_str.replace(',', '.'))
                break
            except ValueError:
                print("Ungültiger Ziel-Notendurchschnitt. Bitte eine Zahl eingeben oder leer lassen.")

        return student_data

    def create_new_studiengang_data(self) -> Dict[str, Any]:
        """
        Erstellt neue Studiengangsdaten basierend auf Benutzereingaben.

        Diese Methode führt den Benutzer durch den Prozess der Erfassung
        aller notwendigen Informationen für einen neuen Studiengang.

        Rückgabe:
            Dictionary mit Studiengangsinformationen
        """
        print("\n" + "=" * 50)
        print("NEUEN STUDIENGANG ERSTELLEN")
        print("=" * 50)

        studiengang_data = {}
        studiengang_data["name"] = input("Name des Studiengangs: ")

        # Erfasse Gesamt-ECTS mit Fehlerbehandlung
        while True:
            gesamtECTS_str = input("Gesamte ECTS (Standard: 180): ")
            if not gesamtECTS_str:
                studiengang_data["gesamtECTS"] = 180
                break
            try:
                studiengang_data["gesamtECTS"] = int(gesamtECTS_str)
                break
            except ValueError:
                print("Ungültige ECTS-Punktzahl. Bitte eine ganze Zahl eingeben oder leer lassen.")

        return studiengang_data