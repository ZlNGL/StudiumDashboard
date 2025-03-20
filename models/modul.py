# models/modul.py
from typing import List, Dict, Any, Optional

from .base_model import BaseModel
from .pruefungsleistung import Pruefungsleistung


class Modul(BaseModel):
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
        super().__init__()  # BaseModel Initialisierung für ID
        self.modulName = modulName
        self.modulID = modulID
        self.beschreibung = beschreibung
        self.ects = ects
        self.semesterZuordnung = semesterZuordnung
        self.pruefungsleistungen = []  # Liste von Pruefungsleistung-Objekten, initial leer
        self.required_for_completion = []  # Liste von Prüfungsarten, die zum Bestehen erforderlich sind (leer = alle)

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
        Prüfungsleistungen als bestanden markiert ist. Falls eine Liste von
        erforderlichen Prüfungsarten angegeben ist, müssen alle diese bestanden sein.

        Parameter:
            student: Das Student-Objekt, für das geprüft werden soll

        Rückgabe:
            True, wenn das Modul vom Studenten abgeschlossen wurde, False sonst
        """
        # Wenn keine Prüfungsleistungen vorhanden sind, ist das Modul nicht bestanden
        if not self.pruefungsleistungen:
            return False

        # Wenn bestimmte Prüfungsarten erforderlich sind
        if self.required_for_completion:
            required_exams = [pl for pl in self.pruefungsleistungen
                              if pl.art in self.required_for_completion]

            # Wenn keine der erforderlichen Prüfungstypen vorhanden sind, verwende Standard-Logik
            if not required_exams:
                return any(pl.bestanden for pl in self.pruefungsleistungen if pl)

            # Alle erforderlichen Prüfungen müssen bestanden sein
            return all(pl.bestanden for pl in required_exams)

        # Standardverhalten: Prüfe, ob mindestens eine Prüfung bestanden ist
        return any(pl.bestanden for pl in self.pruefungsleistungen if pl)

    def add_pruefungsleistung(self, pruefung: Pruefungsleistung) -> None:
        """
        Fügt eine Prüfungsleistung zu diesem Modul hinzu.

        Diese Methode wird verwendet, um neue Prüfungsleistungen wie Klausuren
        oder Hausarbeiten mit diesem Modul zu verknüpfen.

        Parameter:
            pruefung: Das Pruefungsleistung-Objekt, das hinzugefügt werden soll
        """
        if not isinstance(pruefung, Pruefungsleistung):
            raise TypeError("pruefung muss vom Typ Pruefungsleistung sein")

        # Setze die modul_id der Prüfungsleistung auf die ID dieses Moduls
        pruefung.modul_id = self.id
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
        data = super().to_dict()  # BaseModel to_dict aufrufen
        data.update({
            "modulName": self.modulName,
            "modulID": self.modulID,
            "beschreibung": self.beschreibung,
            "ects": self.ects,
            "semesterZuordnung": self.semesterZuordnung,
            "pruefungsleistungen": [pl.to_dict() for pl in self.pruefungsleistungen if pl],
            "required_for_completion": self.required_for_completion
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Modul':
        # Erstelle Modul mit erforderlichen Parametern
        temp_modulName = data.get("modulName", "Temporäres Modul")
        temp_modulID = data.get("modulID", "TEMP")

        modul = cls(
            modulName=temp_modulName,
            modulID=temp_modulID
        )

        # ID aus BaseModel-Daten setzen
        if "id" in data:
            modul.id = data["id"]

        # Restliche Attribute aktualisieren
        modul.beschreibung = data.get("beschreibung", "")
        modul.ects = data.get("ects", 0)
        modul.semesterZuordnung = data.get("semesterZuordnung", 0)
        modul.required_for_completion = data.get("required_for_completion", [])

        # Prüfungsleistungen hinzufügen
        from .pruefungsleistung import Pruefungsleistung
        for pl_data in data.get("pruefungsleistungen", []):
            pruefung = Pruefungsleistung.from_dict(pl_data)
            modul.pruefungsleistungen.append(pruefung)

        return modul