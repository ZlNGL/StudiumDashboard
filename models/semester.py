# models/semester.py
from datetime import date
from typing import List, Dict, Any, Optional

# Import wird durch relative Importe ersetzt
from .modul import Modul


class Semester:
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
        return {
            "nummer": self.nummer,
            "startDatum": self.startDatum.isoformat() if self.startDatum else None,
            "endDatum": self.endDatum.isoformat() if self.endDatum else None,
            "recommendedECTS": self.recommendedECTS,
            "status": self.status,
            "aktiv": self.aktiv,
            "module": [modul.to_dict() for modul in self.module]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Semester':
        """
        Erstellt ein Semester-Objekt aus einem Dictionary.

        Diese Klassenmethode ist das Gegenstück zu to_dict() und ermöglicht die
        Deserialisierung von gespeicherten Semesterdaten inklusive aller
        zugehörigen Module.

        Parameter:
            data: Ein Dictionary mit den Attributen eines Semesters

        Rückgabe:
            Ein neues Semester-Objekt, initialisiert mit den Daten aus dem Dictionary
        """
        semester = cls(
            nummer=data["nummer"],
            startDatum=date.fromisoformat(data["startDatum"]) if data.get("startDatum") else None,
            endDatum=date.fromisoformat(data["endDatum"]) if data.get("endDatum") else None,
            recommendedECTS=data.get("recommendedECTS", 30),
            status=data.get("status", "geplant")
        )
        semester.aktiv = data.get("aktiv", False)

        # Da wir hier einen Import in einer Klassenmethode brauchen,
        # müssen wir ihn hier platzieren, um zirkuläre Importe zu vermeiden
        from .modul import Modul
        for modul_data in data.get("module", []):
            modul = Modul.from_dict(modul_data)
            semester.add_modul(modul)

        return semester