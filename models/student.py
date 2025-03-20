# models/student.py
from datetime import date
from typing import List, Dict, Any, Optional, Tuple

from .base_model import BaseModel
from .person import Person
from .pruefungsleistung import Pruefungsleistung
from .modul import Modul


class Student(Person):
    """
    Klasse zur Repräsentation eines Studenten, erbt von Person.

    Diese Klasse erweitert die Basisklasse Person um studienbezogene Attribute
    und Funktionalitäten. Sie verwaltet die Prüfungsleistungen, ECTS-Fortschritte
    und andere studienbezogene Informationen des Studenten.
    """

    def __init__(self, vorname: str, nachname: str, geburtsdatum: date,
                 matrikelNr: str, email: str = "", immatrikulationsdatum: date = None,
                 zielNotendurchschnitt: float = 2.0, absolvierteECTS: int = 0,
                 fokus: str = "", aktuelleSemesterZahl: int = 1):
        """
        Initialisiert ein Student-Objekt mit den angegebenen Parametern.

        Parameter:
            vorname: Vorname des Studenten
            nachname: Nachname des Studenten
            geburtsdatum: Geburtsdatum des Studenten
            matrikelNr: Matrikelnummer des Studenten
            email: E-Mail-Adresse des Studenten
            immatrikulationsdatum: Datum der Immatrikulation (Einschreibung)
            zielNotendurchschnitt: Angestrebter Notendurchschnitt (Standard: 2.0)
            absolvierteECTS: Bisher erworbene ECTS-Punkte
            fokus: Studienschwerpunkt/-richtung
            aktuelleSemesterZahl: Aktuelle Semesterzahl
        """
        # Ruft den Konstruktor der Elternklasse auf und übergibt die gemeinsamen Attribute
        super().__init__(vorname, nachname, geburtsdatum, email)
        self.matrikelNr = matrikelNr
        # Wenn kein Immatrikulationsdatum angegeben, verwende das heutige Datum
        self.immatrikulationsdatum = immatrikulationsdatum or date.today()
        self.zielNotendurchschnitt = zielNotendurchschnitt
        self.absolvierteECTS = absolvierteECTS
        self.fokus = fokus
        self.aktuelleSemesterZahl = aktuelleSemesterZahl
        self.pruefungsleistungen = []  # Liste aller Prüfungsleistungen, initial leer
        self._bestandene_module_ids = set()  # Set zur Verfolgung bestandener Module-IDs

    def get_durchschnittnote(self) -> float:
        """
        Berechnet den gewichteten Notendurchschnitt des Studenten.

        Diese Methode berücksichtigt nur bestandene Prüfungen und verwendet die
        Gewichtung der einzelnen Noten für die Berechnung des Durchschnitts.

        Rückgabe:
            Der gewichtete Notendurchschnitt oder 0.0, wenn keine bestandenen Prüfungen vorhanden sind
        """
        # Filtere nur bestandene Prüfungen mit vorhandener Note
        passed_exams = [pl for pl in self.pruefungsleistungen if pl.bestanden and pl.note]
        if not passed_exams:
            return 0.0

        # Berechne die Summe der Gewichtungen und die gewichtete Notensumme
        total_weight = sum(pl.note.gewichtung for pl in passed_exams if pl.note)
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(pl.note.get_gewichtete_note() for pl in passed_exams if pl.note)
        return weighted_sum / total_weight

    def get_pruefungsleistungen(self) -> List[Pruefungsleistung]:
        """
        Gibt alle Prüfungsleistungen des Studenten zurück.

        Diese Methode ist nützlich, um auf alle Prüfungsdaten des Studenten zuzugreifen,
        z.B. für die Anzeige in der Benutzeroberfläche oder für Berichte.

        Rückgabe:
            Eine Liste aller Prüfungsleistungen des Studenten
        """
        return self.pruefungsleistungen

    def add_pruefungsleistung(self, pruefung: Pruefungsleistung) -> None:
        """
        Fügt eine Prüfungsleistung zum Studenten hinzu.

        Diese Methode wird verwendet, wenn ein Student eine neue Prüfung ablegt
        oder eine bestehende Prüfung aktualisiert wird.

        Parameter:
            pruefung: Das Pruefungsleistung-Objekt, das hinzugefügt werden soll
        """
        if not isinstance(pruefung, Pruefungsleistung):
            raise TypeError("pruefung muss vom Typ Pruefungsleistung sein")

        self.pruefungsleistungen.append(pruefung)

    def update_ects_for_modul(self, modul: Modul, bestanden: bool) -> None:
        """
        Aktualisiert die ECTS des Studenten basierend auf dem Bestehenstatus eines Moduls.

        Parameter:
            modul: Das Modul-Objekt
            bestanden: Ob das Modul jetzt bestanden ist
        """
        if not modul:
            return

        # Modul als bestanden markieren oder Bestehen aufheben
        if bestanden:
            # Modul wurde bestanden - Prüfen, ob es bereits als bestanden markiert war
            if modul.id not in self._bestandene_module_ids:
                self._bestandene_module_ids.add(modul.id)
                self.absolvierteECTS += modul.ects
        else:
            # Modul ist nicht bestanden - Prüfen, ob es zuvor als bestanden markiert war
            if modul.id in self._bestandene_module_ids:
                self._bestandene_module_ids.remove(modul.id)
                self.absolvierteECTS -= modul.ects

    def get_ects_fortschritt(self) -> int:
        """
        Gibt den aktuellen ECTS-Fortschritt des Studenten zurück.

        Diese Methode ist ein einfacher Getter für die absolvierteECTS-Eigenschaft.

        Rückgabe:
            Die Anzahl der bisher erworbenen ECTS-Punkte
        """
        return self.absolvierteECTS

    def hat_modul_bestanden(self, modul: Modul) -> bool:
        """
        Überprüft, ob der Student ein bestimmtes Modul bestanden hat.

        Diese Methode prüft, ob die modul_id im Set der bestandenen Module enthalten ist
        oder delegiert die Überprüfung an die is_complete_for_student-Methode des Moduls.

        Parameter:
            modul: Das Modul-Objekt, das überprüft werden soll

        Rückgabe:
            True, wenn das Modul vom Studenten bestanden wurde, False sonst
        """
        if modul.id in self._bestandene_module_ids:
            return True
        return modul.is_complete_for_student(self)

    def get_ects_needed(self) -> int:
        """
        Berechnet die noch benötigten ECTS-Punkte bis zum Abschluss.

        Diese Methode geht von einem typischen Bachelor-Studiengang mit
        180 ECTS-Punkten aus. In einer vollständigen Implementierung würde
        dieser Wert vom spezifischen Studiengang abhängen.

        Rückgabe:
            Die Anzahl der noch benötigten ECTS-Punkte (nie negativ)
        """
        return max(0, 180 - self.absolvierteECTS)  # Annahme: 180 ECTS für einen Bachelor-Abschluss

    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert das Student-Objekt in ein Dictionary zur Serialisierung.

        Diese Methode erweitert die to_dict-Methode der Elternklasse um die
        zusätzlichen Attribute des Studenten.

        Rückgabe:
            Ein Dictionary mit den Attributen des Studenten
        """
        # Ruft zuerst die to_dict-Methode der Elternklasse auf
        data = super().to_dict()
        # Fügt die zusätzlichen Attribute des Studenten hinzu
        data.update({
            "matrikelNr": self.matrikelNr,
            "immatrikulationsdatum": self.immatrikulationsdatum.isoformat(),
            "zielNotendurchschnitt": self.zielNotendurchschnitt,
            "absolvierteECTS": self.absolvierteECTS,
            "fokus": self.fokus,
            "aktuelleSemesterZahl": self.aktuelleSemesterZahl,
            "pruefungsleistungen": [pl.to_dict() for pl in self.pruefungsleistungen],
            "_bestandene_module_ids": list(self._bestandene_module_ids)
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Student':
        # Erstelle mit erforderlichen Parametern
        temp_vorname = data.get("vorname", "Temporär")
        temp_nachname = data.get("nachname", "Student")
        temp_geburtsdatum = date.fromisoformat(data.get("geburtsdatum", date.today().isoformat()))
        temp_matrikelNr = data.get("matrikelNr", "000000")

        student = cls(
            vorname=temp_vorname,
            nachname=temp_nachname,
            geburtsdatum=temp_geburtsdatum,
            matrikelNr=temp_matrikelNr
        )

        # ID aus BaseModel-Daten setzen
        if "id" in data:
            student.id = data["id"]

        # Restliche Attribute aktualisieren
        student.email = data.get("email", "")
        student.immatrikulationsdatum = date.fromisoformat(
            data["immatrikulationsdatum"]) if "immatrikulationsdatum" in data else date.today()
        student.zielNotendurchschnitt = data.get("zielNotendurchschnitt", 2.0)
        student.absolvierteECTS = data.get("absolvierteECTS", 0)
        student.fokus = data.get("fokus", "")
        student.aktuelleSemesterZahl = data.get("aktuelleSemesterZahl", 1)
        student._bestandene_module_ids = set(data.get("_bestandene_module_ids", []))

        # Prüfungsleistungen hinzufügen
        from .pruefungsleistung import Pruefungsleistung
        for pl_data in data.get("pruefungsleistungen", []):
            pruefung = Pruefungsleistung.from_dict(pl_data)
            student.pruefungsleistungen.append(pruefung)

        return student