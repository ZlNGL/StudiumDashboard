# models/studiengang.py
from typing import List, Dict, Any, Optional, Tuple

from .base_model import BaseModel
from .semester import Semester
from .modul import Modul


class Studiengang(BaseModel):
    """
    Klasse zur Repräsentation eines Studiengangs.

    Ein Studiengang ist die übergeordnete Einheit, die mehrere Semester
    umfasst und den Rahmen für das gesamte Studium bildet. Diese Klasse verwaltet
    die Semesterstruktur und bietet Methoden zur Analyse des Studienverlaufs.
    """

    def __init__(self, name: str, gesamtECTS: int = 180):
        """
        Initialisiert ein Studiengang-Objekt mit den angegebenen Parametern.

        Parameter:
            name: Name des Studiengangs (z.B. "Informatik Bachelor")
            gesamtECTS: Gesamtzahl der ECTS-Punkte, die für den Abschluss benötigt werden
                        (Standard: 180, typisch für Bachelor-Studiengänge)
        """
        super().__init__()  # BaseModel Initialisierung für ID
        self.name = name
        self.gesamtECTS = gesamtECTS
        self.semester = []  # Liste von Semester-Objekten, initial leer

    def get_fortschritt(self, student) -> float:
        """
        Berechnet den prozentualen Fortschritt eines Studenten im Studiengang.

        Diese Methode dividiert die bisher absolvierten ECTS-Punkte durch die
        Gesamtzahl der benötigten ECTS-Punkte, um den Fortschritt in Prozent zu ermitteln.

        Parameter:
            student: Das Student-Objekt, dessen Fortschritt berechnet werden soll

        Rückgabe:
            Der Fortschritt als Prozentsatz (0.0 bis 100.0)
        """
        if self.gesamtECTS == 0:
            return 0.0  # Vermeidet Division durch Null
        return (student.absolvierteECTS / self.gesamtECTS) * 100

    def add_semester(self, semester: Semester) -> None:
        """
        Fügt ein Semester zum Studiengang hinzu.

        Diese Methode wird verwendet, um die Semesterstruktur des Studiengangs aufzubauen
        oder zu erweitern.

        Parameter:
            semester: Das Semester-Objekt, das hinzugefügt werden soll
        """
        if not isinstance(semester, Semester):
            raise TypeError("semester muss vom Typ Semester sein")

        self.semester.append(semester)

    def get_all_module(self) -> List[Modul]:
        """
        Gibt alle Module des Studiengangs über alle Semester hinweg zurück.

        Diese Methode sammelt alle Module aus allen Semestern des Studiengangs
        und gibt sie als Liste zurück.

        Rückgabe:
            Eine Liste aller Module im Studiengang
        """
        all_modules = []
        for sem in self.semester:
            all_modules.extend(sem.module)
        return all_modules

    def get_semester(self, nummer: int) -> Optional[Semester]:
        """
        Gibt ein bestimmtes Semester anhand seiner Nummer zurück.

        Diese Methode durchsucht die Semesterliste nach einem Semester mit der
        angegebenen Nummer und gibt es, wenn gefunden, zurück.

        Parameter:
            nummer: Die Semesternummer, die gesucht werden soll

        Rückgabe:
            Das gefundene Semester-Objekt oder None, wenn kein Semester
            mit dieser Nummer existiert
        """
        for sem in self.semester:
            if sem.nummer == nummer:
                return sem
        return None

    def get_standort_module(self, student) -> Dict[str, List[Modul]]:
        """
        Gibt den Status aller Module für einen Studenten zurück.

        Diese Methode klassifiziert Module in drei Kategorien:
        - bestanden: Module, die der Student bereits bestanden hat
        - belegt: Module, in denen der Student Prüfungen abgelegt hat, aber (noch) nicht bestanden
        - offen: Module, die der Student noch nicht belegt hat

        Parameter:
            student: Das Student-Objekt, für das der Status der Module ermittelt werden soll

        Rückgabe:
            Ein Dictionary mit den Kategorien als Schlüssel und Listen von Modulen als Werten
        """
        result = {
            "bestanden": [],  # Bereits bestandene Module
            "belegt": [],  # Module, in denen Prüfungen abgelegt wurden, aber (noch) nicht bestanden
            "offen": []  # Noch nicht belegte Module
        }

        # Prüfe, ob der Student existiert
        if not student:
            return result

        for modul in self.get_all_module():
            if not modul:
                continue

            if student.hat_modul_bestanden(modul):
                result["bestanden"].append(modul)
            elif any(pl.modul_id == modul.id for pl in student.pruefungsleistungen if
                     hasattr(pl, 'modul_id') and pl.modul_id):
                result["belegt"].append(modul)
            else:
                result["offen"].append(modul)

        return result

    def get_gesamt_note(self, student) -> float:
        """
        Berechnet die Gesamtnote eines Studenten in diesem Studiengang.

        Diese Methode delegiert die Berechnung an die get_durchschnittnote-Methode
        des Studenten, da diese die spezifischen Regeln für die Notenberechnung enthält.

        Parameter:
            student: Das Student-Objekt, dessen Gesamtnote berechnet werden soll

        Rückgabe:
            Die Gesamtnote des Studenten
        """
        if not student:
            return 0.0
        return student.get_durchschnittnote()

    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert das Studiengang-Objekt in ein Dictionary zur Serialisierung.

        Diese Methode ist wichtig für die Speicherung der Daten und wandelt
        alle komplexen Typen in serialisierbare Formate um.

        Rückgabe:
            Ein Dictionary mit den Attributen des Studiengangs und seiner Semester
        """
        data = super().to_dict()  # BaseModel to_dict aufrufen
        data.update({
            "name": self.name,
            "gesamtECTS": self.gesamtECTS,
            "semester": [sem.to_dict() for sem in self.semester]
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Studiengang':
        """
        Erstellt ein Studiengang-Objekt aus einem Dictionary.
        """
        # Erst ein vollständiges Objekt mit dem Namen erstellen
        temp_name = data.get("name", "Temporärer Name")
        studiengang = cls(name=temp_name)

        # ID aus BaseModel-Daten setzen
        if "id" in data:
            studiengang.id = data["id"]

        # Attribute aktualisieren
        studiengang.name = data.get("name", temp_name)
        studiengang.gesamtECTS = data.get("gesamtECTS", 180)

        # Semester hinzufügen
        from .semester import Semester
        for sem_data in data.get("semester", []):
            studiengang.add_semester(Semester.from_dict(sem_data))

        return studiengang