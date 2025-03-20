# models/semester.py
from datetime import date
from typing import List, Dict, Any, Optional

from .base_model import BaseModel
from .modul import Modul


class Semester(BaseModel):
    """
    Klasse zur Repräsentation eines Semesters in einem Studiengang.

    Ein Semester ist ein zeitlicher Abschnitt im Studium, der typischerweise mehrere
    Module umfasst. Diese Klasse speichert sowohl zeitliche Informationen als auch die
    zugehörigen Module und verwaltet deren Beziehungen zum Semester.
    """

    def __init__(self, nummer: int, startDatum: date = None, endDatum: date = None,
                 recommendedECTS: int = 30, status: str = "geplant"):
        """
        Initialisiert ein Semester-Objekt mit den angegebenen Parametern.

        Parameter:
            nummer: Die Semesternummer (1, 2, usw.)
            startDatum: Startdatum des Semesters
            endDatum: Enddatum des Semesters
            recommendedECTS: Empfohlene ECTS-Punkte für dieses Semester (Standard: 30)
            status: Status des Semesters (z.B. "geplant", "aktiv", "abgeschlossen")
        """
        super().__init__()  # BaseModel Initialisierung für ID
        self.nummer = nummer
        self.startDatum = startDatum
        self.endDatum = endDatum
        self.recommendedECTS = recommendedECTS
        self.status = status
        self.aktiv = False  # Flag, ob das Semester aktuell aktiv ist
        self.module = []  # Liste von Modul-Objekten, initial leer

    def get_dauer(self) -> int:
        """
        Berechnet die Dauer des Semesters in Tagen.

        Rückgabe:
            Die Anzahl der Tage zwischen Start- und Enddatum, oder 0 wenn eines
            der Daten nicht gesetzt ist
        """
        if not (self.startDatum and self.endDatum):
            return 0
        return (self.endDatum - self.startDatum).days

    def add_modul(self, modul: Modul) -> None:
        """
        Fügt ein Modul zu diesem Semester hinzu.

        Diese Methode ermöglicht die Zuordnung von Modulen zu einem bestimmten Semester
        und erweitert damit die Semesterstruktur.

        Parameter:
            modul: Das Modul-Objekt, das diesem Semester hinzugefügt werden soll
        """
        if not isinstance(modul, Modul):
            raise TypeError("modul muss vom Typ Modul sein")

        self.module.append(modul)

    def is_active(self) -> bool:
        """
        Überprüft, ob das Semester aktuell aktiv ist.

        Ein Semester gilt als aktiv, wenn das aktuelle Datum zwischen dem
        Start- und Enddatum liegt, oder wenn das 'aktiv'-Flag gesetzt ist.

        Rückgabe:
            True, wenn das Semester aktiv ist, False sonst
        """
        today = date.today()
        if not (self.startDatum and self.endDatum):
            return self.aktiv  # Wenn keine Daten gesetzt sind, verwende das Flag
        return self.startDatum <= today <= self.endDatum

    def get_remaining_ects(self) -> int:
        """
        Berechnet die verbleibenden ECTS-Punkte, die noch zu absolvieren sind.

        Diese Methode bestimmt die Differenz zwischen den empfohlenen ECTS-Punkten
        und den bereits durch abgeschlossene Module erworbenen Punkten.

        Rückgabe:
            Die Anzahl der noch zu erwerbenden ECTS-Punkte (nie negativ)
        """
        completed_ects = sum(modul.get_ects() for modul in self.module if modul.is_complete_for_student(None))
        return max(0, self.recommendedECTS - completed_ects)  # Stelle sicher, dass das Ergebnis nicht negativ ist

    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert das Semester-Objekt in ein Dictionary zur Serialisierung.

        Diese Methode ist wichtig für die Persistenz der Daten und wandelt alle
        komplexen Typen (wie date-Objekte) in serialisierbare Formate um.

        Rückgabe:
            Ein Dictionary mit den Attributen des Semesters und seiner Module
        """
        data = super().to_dict()  # BaseModel to_dict aufrufen
        data.update({
            "nummer": self.nummer,
            "startDatum": self.startDatum.isoformat() if self.startDatum else None,
            "endDatum": self.endDatum.isoformat() if self.endDatum else None,
            "recommendedECTS": self.recommendedECTS,
            "status": self.status,
            "aktiv": self.aktiv,
            "module": [modul.to_dict() for modul in self.module]
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Semester':
        # Erst mit der Semesternummer erstellen
        temp_nummer = data.get("nummer", 1)
        semester = cls(nummer=temp_nummer)

        # ID aus BaseModel-Daten setzen
        if "id" in data:
            semester.id = data["id"]

        # Restliche Attribute setzen
        semester.startDatum = date.fromisoformat(data["startDatum"]) if data.get("startDatum") else None
        semester.endDatum = date.fromisoformat(data["endDatum"]) if data.get("endDatum") else None
        semester.recommendedECTS = data.get("recommendedECTS", 30)
        semester.status = data.get("status", "geplant")
        semester.aktiv = data.get("aktiv", False)

        # Module hinzufügen
        from .modul import Modul
        for modul_data in data.get("module", []):
            modul = Modul.from_dict(modul_data)
            semester.add_modul(modul)

        return semester