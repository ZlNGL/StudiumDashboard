# models/modul.py
from typing import List, Dict, Any, Optional

# Import wird durch relative Importe ersetzt
from .pruefungsleistung import Pruefungsleistung


class Modul:
    """
    Klasse zur Repräsentation eines Moduls in einem Studiengang.

    Ein Modul ist eine Lehreinheit im Studium, die typischerweise aus einer
    oder mehreren Prüfungsleistungen besteht und ECTS-Punkte vergibt.
    Diese Klasse verwaltet die zugehörigen Daten und Beziehungen.
    """

    def __init__(self, modulName: str, modulID: str, beschreibung: str = "",
                 ects: int = 0, semesterZuordnung: int = 0):
        """
        Initialisiert ein Modul-Objekt mit den angegebenen Parametern.

        Parameter:
            modulName: Name des Moduls (z.B. "Programmierung 1")
            modulID: Eindeutige Kennung für das Modul (z.B. "INF101")
            beschreibung: Ausführliche Beschreibung des Moduls
            ects: ECTS-Punkte/Credits für dieses Modul
            semesterZuordnung: Semester, in dem das Modul typischerweise belegt wird
        """
        self.modulName = modulName
        self.modulID = modulID
        self.beschreibung = beschreibung
        self.ects = ects
        self.semesterZuordnung = semesterZuordnung
        self.pruefungsleistungen = []  # Liste von Pruefungsleistung-Objekten, initial leer

    def get_ects(self) -> int:
        """
        Gibt die ECTS-Punkte für dieses Modul zurück.

        Rückgabe:
            Die Anzahl der ECTS-Punkte als Ganzzahl
        """
        return self.ects

    def get_name(self) -> str:
        """
        Gibt den Namen des Moduls zurück.

        Rückgabe:
            Der Name des Moduls als Zeichenkette
        """
        return self.modulName

    def is_complete_for_student(self, student) -> bool:
        """
        Überprüft, ob das Modul für einen bestimmten Studenten abgeschlossen ist.

        Ein Modul gilt als abgeschlossen, wenn mindestens eine der zugehörigen
        Prüfungsleistungen als bestanden markiert ist. In der Praxis könnte
        hier eine komplexere Logik implementiert werden.

        Parameter:
            student: Das Student-Objekt, für das geprüft werden soll

        Rückgabe:
            True, wenn das Modul vom Studenten abgeschlossen wurde, False sonst
        """
        # Einfache Implementierung: Prüfen, ob mindestens eine Prüfung bestanden ist
        return any(pl.bestanden for pl in self.pruefungsleistungen if pl)

    def add_pruefungsleistung(self, pruefung: Pruefungsleistung) -> None:
        """
        Fügt eine Prüfungsleistung zu diesem Modul hinzu.

        Diese Methode wird verwendet, um neue Prüfungsleistungen wie Klausuren
        oder Hausarbeiten mit diesem Modul zu verknüpfen.

        Parameter:
            pruefung: Das Pruefungsleistung-Objekt, das hinzugefügt werden soll
        """
        if pruefung:
            self.pruefungsleistungen.append(pruefung)

    def get_current_grade(self) -> float:
        """
        Berechnet die aktuelle Note für dieses Modul basierend auf allen Prüfungen.

        Die Berechnung berücksichtigt die Gewichtung der einzelnen Noten.
        Nur bestandene Prüfungen werden in die Berechnung einbezogen.

        Rückgabe:
            Die gewichtete Durchschnittsnote oder 0.0, wenn keine bestandenen Prüfungen vorhanden sind
        """
        passed_exams = [pl for pl in self.pruefungsleistungen if pl and pl.bestanden]
        if not passed_exams:
            return 0.0

        total_weight = sum(pl.note.gewichtung for pl in passed_exams if pl.note)
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(pl.note.get_gewichtete_note() for pl in passed_exams if pl.note)
        return weighted_sum / total_weight

    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert das Modul-Objekt in ein Dictionary zur Serialisierung.

        Diese Methode ist wichtig für die Persistenz der Daten, z.B. wenn sie
        in einer JSON-Datei gespeichert werden sollen.

        Rückgabe:
            Ein Dictionary mit den Attributen des Moduls
        """
        return {
            "modulName": self.modulName,
            "modulID": self.modulID,
            "beschreibung": self.beschreibung,
            "ects": self.ects,
            "semesterZuordnung": self.semesterZuordnung,
            "pruefungsleistungen": [pl.to_dict() for pl in self.pruefungsleistungen if pl]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Modul':
        """
        Erstellt ein Modul-Objekt aus einem Dictionary.

        Diese Klassenmethode ist das Gegenstück zu to_dict() und ermöglicht die
        Deserialisierung von gespeicherten Moduldaten.

        Parameter:
            data: Ein Dictionary mit den Attributen eines Moduls

        Rückgabe:
            Ein neues Modul-Objekt, initialisiert mit den Daten aus dem Dictionary
        """
        modul = cls(
            modulName=data["modulName"],
            modulID=data["modulID"],
            beschreibung=data.get("beschreibung", ""),
            ects=data.get("ects", 0),
            semesterZuordnung=data.get("semesterZuordnung", 0)
        )

        # Da wir hier einen Import in einer Klassenmethode brauchen,
        # müssen wir ihn hier platzieren, um zirkuläre Importe zu vermeiden
        from .pruefungsleistung import Pruefungsleistung
        for pl_data in data.get("pruefungsleistungen", []):
            modul.pruefungsleistungen.append(Pruefungsleistung.from_dict(pl_data))

        return modul