# controllers/dashboard.py
from datetime import date, timedelta
from typing import List, Dict, Optional, Tuple, Set, Union, Any

# Importe für Modellklassen
from models import Student, Studiengang, Semester, Modul, Pruefungsleistung, Note
# Import für DatenManager
from .datenmanager import DatenManager


class Dashboard:
    """
    Zentrale Controller-Klasse, die alle Komponenten verbindet und die Berechnungen
    und Aktualisierungen von Kennzahlen wie Notendurchschnitt und ECTS-Fortschritt verwaltet.

    Das Dashboard fungiert als Vermittler zwischen den Modellklassen (Datenstruktur),
    dem DatenManager (Persistenz) und den Visualisierungs- und Interaktionskomponenten.
    Es stellt die Geschäftslogik der Anwendung bereit.
    """

    def __init__(self, daten_manager: DatenManager = None):
        """
        Initialisiert ein Dashboard-Objekt mit dem angegebenen DatenManager.

        Parameter:
            daten_manager: Das DatenManager-Objekt für Datenoperationen (optional)
                           Falls nicht angegeben, wird ein neuer DatenManager erstellt
        """
        # Wenn kein DatenManager übergeben wird, erstelle einen neuen
        self.daten_manager = daten_manager or DatenManager()
        self.studiengang = None  # Wird später bei der Initialisierung gesetzt
        self.student = None  # Wird später bei der Initialisierung gesetzt
        self.benutzerinteraktion = None  # Wird später von außen gesetzt
        self.visualisierung = None  # Wird später von außen gesetzt

    def initialisieren(self) -> bool:
        """
        Initialisiert das Dashboard durch Laden vorhandener Daten oder Erstellen neuer Objekte.

        Diese Methode versucht, bestehende Daten über den DatenManager zu laden.
        Falls keine Daten vorhanden sind, gibt sie False zurück, was signalisiert,
        dass neue Daten erstellt werden müssen.

        Rückgabe:
            True, wenn die Initialisierung erfolgreich war, False sonst
        """
        # Versuche, bestehende Daten zu laden
        self.studiengang, self.student = self.daten_manager.laden()

        # Wenn keine Daten existieren, gib False zurück
        if not (self.studiengang and self.student):
            return False

        return True

    def create_new_data(self, student_data: Dict[str, Any], studiengang_data: Dict[str, Any]) -> bool:
        """
        Erstellt neue Studenten- und Studiengangsdaten.

        Diese Methode wird aufgerufen, wenn keine bestehenden Daten geladen werden
        konnten und neue Daten basierend auf Benutzereingaben erstellt werden müssen.

        Parameter:
            student_data: Dictionary mit Studenteninformationen
            studiengang_data: Dictionary mit Studiengangsinformationen

        Rückgabe:
            True, wenn die Erstellung erfolgreich war, False sonst
        """
        try:
            # Erstelle Studenten
            self.student = Student(
                vorname=student_data.get("vorname", ""),
                nachname=student_data.get("nachname", ""),
                geburtsdatum=student_data.get("geburtsdatum", date.today()),
                matrikelNr=student_data.get("matrikelNr", ""),
                email=student_data.get("email", ""),
                zielNotendurchschnitt=float(student_data.get("zielNotendurchschnitt", 2.0))
            )

            # Erstelle Studiengang
            self.studiengang = Studiengang(
                name=studiengang_data.get("name", ""),
                gesamtECTS=int(studiengang_data.get("gesamtECTS", 180))
            )

            # Speichere die Daten
            return self.daten_manager.speichern(self.studiengang, self.student)
        except Exception as e:
            print(f"Fehler beim Erstellen neuer Daten: {e}")
            return False

    def aktualisieren(self) -> bool:
        """
        Aktualisiert das Dashboard durch Speichern der aktuellen Daten.

        Diese Methode wird nach Änderungen an den Daten aufgerufen,
        um die aktuellen Zustände zu persistieren.

        Rückgabe:
            True, wenn die Aktualisierung erfolgreich war, False sonst
        """
        if not (self.studiengang and self.student):
            print("Keine Daten zum Aktualisieren vorhanden.")
            return False

        return self.daten_manager.speichern(self.studiengang, self.student)

    def berechne_notendurchschnitt(self) -> float:
        """
        Berechnet den aktuellen Notendurchschnitt.

        Diese Methode delegiert die Berechnung an die get_durchschnittnote-Methode
        des Studenten, falls dieser existiert.

        Rückgabe:
            Der aktuelle Notendurchschnitt oder 0.0, wenn kein Student vorhanden ist
        """
        if not self.student:
            return 0.0

        return self.student.get_durchschnittnote()

    def berechne_ects_fortschritt(self) -> Dict[str, Union[int, float]]:
        """
        Berechnet den aktuellen ECTS-Fortschritt.

        Diese Methode erstellt ein umfassendes Dictionary mit Informationen
        zum ECTS-Fortschritt, das für die Anzeige in der Benutzeroberfläche
        oder für Berichte verwendet werden kann.

        Rückgabe:
            Ein Dictionary mit Informationen zum ECTS-Fortschritt:
            - 'absolut': Anzahl der absolvierten ECTS
            - 'gesamt': Gesamtzahl der benötigten ECTS
            - 'prozent': Prozentualer Fortschritt
        """
        if not (self.studiengang and self.student):
            return {"absolut": 0, "gesamt": 0, "prozent": 0.0}

        absolut = self.student.get_ects_fortschritt()
        gesamt = self.studiengang.gesamtECTS
        prozent = (absolut / gesamt) * 100 if gesamt > 0 else 0.0

        return {
            "absolut": absolut,
            "gesamt": gesamt,
            "prozent": round(prozent, 2)  # Runde auf 2 Nachkommastellen für die Anzeige
        }

    def zeige_notenverteilung(self) -> Dict[str, int]:
        """
        Ermittelt die Verteilung der Noten.

        Diese Methode zählt das Vorkommen jeder Note in den Prüfungsleistungen
        des Studenten und erstellt daraus eine statistische Verteilung.

        Rückgabe:
            Ein Dictionary mit Noten als Schlüssel und ihrer Häufigkeit als Werte
        """
        if not self.student:
            return {}

        pruefungen = self.student.get_pruefungsleistungen()
        verteilung = {}

        # Zähle das Vorkommen jeder Note
        for pruefung in pruefungen:
            if pruefung.note:
                note = str(pruefung.note.wert)
                verteilung[note] = verteilung.get(note, 0) + 1

        return verteilung

    def anstehende_pruefungen(self, tage: int = 30) -> List[Pruefungsleistung]:
        """
        Ermittelt anstehende Prüfungen innerhalb eines bestimmten Zeitraums.

        Diese Methode durchsucht alle Module nach Prüfungen, deren Datum
        innerhalb des angegebenen Zeitraums liegt und die noch nicht bestanden sind.

        Parameter:
            tage: Anzahl der Tage, die vorausgeschaut werden soll (Standard: 30)

        Rückgabe:
            Eine Liste anstehender Pruefungsleistung-Objekte
        """
        if not self.studiengang:
            return []

        today = date.today()
        end_date = today + timedelta(days=tage)

        upcoming = []
        for modul in self.studiengang.get_all_module():
            for pruefung in modul.pruefungsleistungen:
                # Filtere Prüfungen, die im angegebenen Zeitraum liegen und nicht bestanden sind
                if pruefung.datum and today <= pruefung.datum <= end_date and not pruefung.bestanden:
                    upcoming.append(pruefung)

        # Sortiere nach Datum
        upcoming.sort(key=lambda p: p.datum if p.datum else date.max)
        return upcoming

    def zeige_semesterdurchschnitte(self) -> Dict[int, float]:
        """
        Berechnet den durchschnittlichen Notendurchschnitt für jedes Semester.

        Diese Methode gruppiert die Noten nach Semestern und berechnet
        für jedes Semester einen gewichteten Durchschnitt.

        Rückgabe:
            Ein Dictionary mit Semesternummern als Schlüssel und
            Durchschnittsnoten als Werte
        """
        if not (self.studiengang and self.student):
            return {}

        semester_noten = {}

        # Durchlaufe alle Semester
        for sem in self.studiengang.semester:
            noten = []
            # Sammle alle Noten aus den Modulen dieses Semesters
            for modul in sem.module:
                for pruefung in modul.pruefungsleistungen:
                    if pruefung.bestanden and pruefung.note:
                        noten.append((pruefung.note.wert, pruefung.note.gewichtung))

            # Berechne den gewichteten Durchschnitt für dieses Semester
            if noten:
                gewichtete_summe = sum(note * gewicht for note, gewicht in noten)
                gesamt_gewicht = sum(gewicht for _, gewicht in noten)
                semester_noten[sem.nummer] = round(gewichtete_summe / gesamt_gewicht, 2) if gesamt_gewicht > 0 else 0.0
            else:
                semester_noten[sem.nummer] = 0.0

        return semester_noten

    def erfasse_note(self, modul_name: str, pruefung_data: Dict[str, Any]) -> bool:
        """
        Erfasst eine neue Note für ein Modul.

        Diese Methode erstellt eine neue Prüfungsleistung mit der angegebenen Note
        und fügt sie dem entsprechenden Modul und dem Studenten hinzu.

        Parameter:
            modul_name: Name des Moduls
            pruefung_data: Dictionary mit Prüfungsinformationen

        Rückgabe:
            True, wenn die Erfassung erfolgreich war, False sonst
        """
        if not (self.studiengang and self.student):
            return False

        # Finde das Modul
        target_modul = None
        for modul in self.studiengang.get_all_module():
            if modul.modulName == modul_name:
                target_modul = modul
                break

        if not target_modul:
            print(f"Modul '{modul_name}' nicht gefunden.")
            return False

        try:
            # Erstelle Prüfungsleistung
            pruefung = Pruefungsleistung(
                art=pruefung_data.get("art", "Klausur"),
                datum=pruefung_data.get("datum", date.today()),
                beschreibung=pruefung_data.get("beschreibung", "")
            )

            # Erstelle Note
            note = Note(
                typ=pruefung_data.get("typ", "Note"),
                wert=float(pruefung_data.get("wert", 0)),
                gewichtung=float(pruefung_data.get("gewichtung", 1.0))
            )

            # Setze Note für die Prüfungsleistung
            pruefung.set_note(note)

            # Füge zum Modul und zum Studenten hinzu
            target_modul.add_pruefungsleistung(pruefung)
            self.student.add_pruefungsleistung(pruefung)

            # Aktualisiere ECTS, wenn bestanden
            if pruefung.bestanden:
                self.student.absolvierteECTS += target_modul.ects

            # Speichere Änderungen
            return self.aktualisieren()
        except Exception as e:
            print(f"Fehler beim Erfassen der Note: {e}")
            return False

    def speichern(self) -> bool:
        """
        Speichert die aktuellen Daten.

        Diese Methode ist ein Wrapper für die speichern-Methode des DatenManagers
        und bietet eine einfache Schnittstelle zum Speichern des aktuellen Zustands.

        Rückgabe:
            True, wenn das Speichern erfolgreich war, False sonst
        """
        if not (self.studiengang and self.student):
            print("Keine Daten zum Speichern vorhanden.")
            return False

        return self.daten_manager.speichern(self.studiengang, self.student)

    def erfasse_modul(self, semester_nummer: int, modul_data: Dict[str, Any]) -> bool:
        """
        Erfasst ein neues Modul für ein Semester.

        Diese Methode erstellt ein neues Modul mit den angegebenen Daten
        und fügt es dem entsprechenden Semester hinzu. Falls das Semester
        nicht existiert, wird es erstellt.

        Parameter:
            semester_nummer: Nummer des Semesters
            modul_data: Dictionary mit Modulinformationen

        Rückgabe:
            True, wenn die Erfassung erfolgreich war, False sonst
        """
        if not self.studiengang:
            return False

        # Finde oder erstelle das Semester
        semester = self.studiengang.get_semester(semester_nummer)
        if not semester:
            print(f"Semester {semester_nummer} nicht gefunden. Erstelle neu.")
            semester = Semester(nummer=semester_nummer)
            self.studiengang.add_semester(semester)

        try:
            # Erstelle Modul
            modul = Modul(
                modulName=modul_data.get("name", "Unbekanntes Modul"),
                modulID=modul_data.get("id", f"M{len(semester.module) + 1}"),
                beschreibung=modul_data.get("beschreibung", ""),
                ects=int(modul_data.get("ects", 5)),
                semesterZuordnung=semester_nummer
            )

            # Füge zum Semester hinzu
            semester.add_modul(modul)

            # Speichere Änderungen
            return self.aktualisieren()
        except Exception as e:
            print(f"Fehler beim Erfassen des Moduls: {e}")
            return False

    def bearbeite_ziele(self, ziel_durchschnitt: float) -> bool:
        """
        Aktualisiert den Ziel-Notendurchschnitt.

        Diese Methode setzt den Ziel-Notendurchschnitt des Studenten
        auf den angegebenen Wert und speichert die Änderung.

        Parameter:
            ziel_durchschnitt: Neuer Ziel-Notendurchschnitt

        Rückgabe:
            True, wenn die Aktualisierung erfolgreich war, False sonst
        """
        if not self.student:
            return False

        try:
            self.student.zielNotendurchschnitt = float(ziel_durchschnitt)
            return self.aktualisieren()
        except Exception as e:
            print(f"Fehler beim Bearbeiten des Ziels: {e}")
            return False

    def exportiere_daten(self, export_pfad: str = "noten_export.csv") -> bool:
        """
        Exportiert Daten in eine CSV-Datei.

        Diese Methode ist ein Wrapper für die export_csv-Methode des DatenManagers
        und ermöglicht den Export von Studentendaten in eine CSV-Datei.

        Parameter:
            export_pfad: Pfad zur Export-Datei (Standard: "noten_export.csv")

        Rückgabe:
            True, wenn der Export erfolgreich war, False sonst
        """
        if not self.student:
            return False

        return self.daten_manager.export_csv(self.student, export_pfad)

    def importiere_daten(self, import_pfad: str) -> bool:
        """
        Importiert Daten aus einer CSV-Datei.

        Diese Methode ist ein Wrapper für die import_csv-Methode des DatenManagers
        und ermöglicht den Import von Daten aus einer CSV-Datei.

        Parameter:
            import_pfad: Pfad zur Import-Datei

        Rückgabe:
            True, wenn der Import erfolgreich war, False sonst
        """
        if not (self.studiengang and self.student):
            return False

        return self.daten_manager.import_csv(self.student, self.studiengang, import_pfad)
