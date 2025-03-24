# models/person.py
from datetime import date
from typing import Dict, Any

from .base_model import BaseModel

class Person(BaseModel):
    """
    Basisklasse zur Repräsentation einer Person.
    Diese Klasse ist als abstrakte Basisklasse implementiert, die erweitert werden kann,
    um beispielsweise spezifische Personentypen wie Studenten oder Professoren zu erstellen.
    Sie enthält grundlegende Attribute und Methoden, die für alle Personentypen relevant sind.
    """

    def __init__(self, vorname: str, nachname: str, geburtsdatum: date, email: str = ""):
        """
        Initialisiert ein Person-Objekt mit grundlegenden persönlichen Daten.

        Parameter:
            vorname: Vorname der Person
            nachname: Nachname der Person
            geburtsdatum: Geburtsdatum als date-Objekt
            email: E-Mail-Adresse (optional, Standardwert ist ein leerer String)
        """
        super().__init__()  # BaseModel Initialisierung für ID
        self.vorname = vorname
        self.nachname = nachname
        self.geburtsdatum = geburtsdatum
        self.email = email

    def get_fullname(self) -> str:
        """
        Gibt den vollständigen Namen der Person zurück.

        Rückgabe:
            Eine Zeichenkette bestehend aus Vor- und Nachname, getrennt durch ein Leerzeichen
        """
        return f"{self.vorname} {self.nachname}"

    def set_vorname(self, vorname: str) -> None:
        """
        Setzt den Vornamen der Person.

        Parameter:
            vorname: Der neue Vorname der Person
        """
        self.vorname = vorname

    def set_nachname(self, nachname: str) -> None:
        """
        Setzt den Nachnamen der Person.

        Parameter:
            nachname: Der neue Nachname der Person
        """
        self.nachname = nachname

    def set_email(self, email: str) -> None:
        """
        Setzt die E-Mail-Adresse der Person.

        Parameter:
            email: Die neue E-Mail-Adresse der Person
        """
        self.email = email

    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert das Person-Objekt in ein Dictionary zur Serialisierung.
        Dies ist nützlich für die Speicherung der Daten.

        Rückgabe:
            Ein Dictionary mit den Attributen der Person
        """
        data = super().to_dict()  # BaseModel to_dict aufrufen
        data.update({
            "vorname": self.vorname,
            "nachname": self.nachname,
            "geburtsdatum": self.geburtsdatum.isoformat(),  # ISO-Format für bessere Kompatibilität
            "email": self.email
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Person':
        """
        Erstellt ein Person-Objekt aus einem Dictionary.
        Diese Klassenmethode ist das Gegenstück zu to_dict() und ermöglicht die
        Deserialisierung von gespeicherten Personendaten.

        Parameter:
            data: Ein Dictionary mit den Attributen einer Person

        Rückgabe:
            Ein neues Person-Objekt, initialisiert mit den Daten aus dem Dictionary
        """
        person = super().from_dict(data)  # BaseModel from_dict aufrufen
        person.vorname = data["vorname"]
        person.nachname = data["nachname"]
        person.geburtsdatum = date.fromisoformat(data["geburtsdatum"])  # Konvertierung aus ISO-Format
        person.email = data.get("email", "")  # Verwendet get(), um sicher auf optionale Werte zuzugreifen
        return person