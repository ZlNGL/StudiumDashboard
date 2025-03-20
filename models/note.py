# models/note.py
from datetime import date
from typing import Dict, Any

from .base_model import BaseModel

class Note(BaseModel):
    """
    Klasse zur Repräsentation einer Note.

    Diese Klasse speichert alle Informationen zu einer Note, einschließlich ihres Werts,
    ihrer Gewichtung und zusätzlicher Metadaten wie Datum und Kommentare. Sie bietet
    auch Methoden zur Berechnung gewichteter Noten und Bestehensüberprüfungen.
    """

    def __init__(self, typ: str, wert: float, gewichtung: float = 1.0,
                 datum: date = None, kommentar: str = "", punkte: int = 0):
        """
        Initialisiert ein Note-Objekt mit den angegebenen Parametern.

        Parameter:
            typ: Art der Note (z.B. "Klausur", "Hausarbeit")
            wert: Der Notenwert (z.B. 1.7, 2.3)
            gewichtung: Gewichtung der Note (Standard: 1.0)
            datum: Datum, an dem die Note erhalten wurde (Standard: aktuelles Datum)
            kommentar: Zusätzlicher Kommentar zur Note
            punkte: Erreichte Punktzahl (für alternative Bewertungssysteme)
        """
        super().__init__()  # BaseModel Initialisierung für ID
        self.typ = typ
        self.wert = wert
        self.gewichtung = gewichtung
        self.datum = datum if datum else date.today()  # Wenn kein Datum angegeben, heutiges Datum verwenden
        self.kommentar = kommentar
        self.punkte = punkte

    def get_gewichtete_note(self) -> float:
        """
        Berechnet und gibt die gewichtete Note zurück.
        Die gewichtete Note ist das Produkt aus dem Notenwert und der Gewichtung.
        Diese wird für die Berechnung des Durchschnitts über mehrere Noten verwendet.

        Rückgabe:
            Der gewichtete Notenwert
        """
        return self.wert * self.gewichtung

    def is_passed(self, grenze: float = 4.0) -> bool:
        """
        Überprüft, ob die Note als bestanden gilt.

        Im deutschen Notensystem sind Noten von 1.0 bis 4.0 bestanden,
        während Noten größer als 4.0 als nicht bestanden gelten.

        Parameter:
            grenze: Der Schwellenwert für das Bestehen (Standard: 4.0 im deutschen Notensystem)

        Rückgabe:
            True, wenn die Note bestanden ist, False sonst
        """
        return self.wert <= grenze

    def convert_to_points(self) -> int:
        """
        Konvertiert die Note in einen Punktwert.
        Dies ist nützlich für Systeme, die mit Punkten statt mit Noten arbeiten.

        Rückgabe:
            Der gespeicherte Punktwert
        """
        return self.punkte

    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert das Note-Objekt in ein Dictionary zur Serialisierung.
        Dies ermöglicht die einfache Speicherung in Dateiformaten wie JSON.

        Rückgabe:
            Ein Dictionary mit den Attributen der Note
        """
        data = super().to_dict()  # BaseModel to_dict aufrufen
        data.update({
            "typ": self.typ,
            "wert": self.wert,
            "gewichtung": self.gewichtung,
            "datum": self.datum.isoformat(),  # ISO-Format für bessere Kompatibilität
            "kommentar": self.kommentar,
            "punkte": self.punkte
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Note':
        # Erstelle Note mit erforderlichen Parametern
        temp_typ = data.get("typ", "Unbekannt")
        temp_wert = data.get("wert", 4.0)

        note = cls(
            typ=temp_typ,
            wert=temp_wert
        )

        # ID aus BaseModel-Daten setzen
        if "id" in data:
            note.id = data["id"]

        # Restliche Attribute aktualisieren
        note.gewichtung = data.get("gewichtung", 1.0)
        note.datum = date.fromisoformat(data["datum"]) if "datum" in data else date.today()
        note.kommentar = data.get("kommentar", "")
        note.punkte = data.get("punkte", 0)

        return note