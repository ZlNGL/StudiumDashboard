# models/pruefungsleistung.py
from datetime import date
from typing import Dict, Any, Optional

# Import wird durch relative Importe ersetzt
from .note import Note


class Pruefungsleistung:
    """
    Klasse zur Repräsentation einer Prüfungsleistung.

    Diese Klasse modelliert eine konkrete Prüfungsleistung wie eine Klausur, Hausarbeit oder
    mündliche Prüfung. Sie speichert sowohl allgemeine Informationen zur Prüfung als auch
    die damit verbundene Note (falls vorhanden) und den Bestehens-Status.
    """

    def __init__(self, art: str, datum: date = None,
                 beschreibung: str = "", deadline: date = None,
                 versuche: int = 1, anmerkung: str = ""):
        """
        Initialisiert ein Pruefungsleistung-Objekt mit den angegebenen Parametern.

        Parameter:
            art: Art der Prüfung (z.B. "Klausur", "Hausarbeit", "mündliche Prüfung")
            datum: Datum der Prüfung (Standard: aktuelles Datum, wenn nicht angegeben)
            beschreibung: Beschreibung der Prüfung (z.B. "Zwischenprüfung Modul XYZ")
            deadline: Abgabefrist (relevant für Hausarbeiten oder Projekte)
            versuche: Anzahl der bisherigen Versuche (Standard: 1)
            anmerkung: Zusätzliche Anmerkungen zur Prüfung
        """
        self.art = art
        self.datum = datum if datum else date.today()  # Wenn kein Datum angegeben, heutiges Datum verwenden
        self.beschreibung = beschreibung
        self.deadline = deadline
        self.versuche = versuche
        self.anmerkung = anmerkung
        self.note = None  # Referenz auf ein Note-Objekt, initial None (keine Note vorhanden)
        self.bestanden = False  # Initial als nicht bestanden markiert

    def set_note(self, note: Note) -> None:
        """
        Setzt die Note für diese Prüfungsleistung und aktualisiert den Bestehens-Status.

        Wenn eine Note gesetzt wird, wird automatisch der Bestehens-Status basierend auf der Note
        aktualisiert. Das vermeidet inkonsistente Zustände zwischen Note und Bestehens-Status.

        Parameter:
            note: Das Note-Objekt, das die Bewertung für diese Prüfung repräsentiert
        """
        self.note = note
        self.bestanden = note.is_passed() if note else False  # Bestehens-Status aus der Note ableiten

    def get_detail_info(self) -> Dict[str, Any]:
        """
        Gibt detaillierte Informationen über die Prüfungsleistung zurück.

        Diese Methode ist nützlich für die Anzeige von Prüfungsdetails in der
        Benutzeroberfläche oder für Berichte.

        Rückgabe:
            Ein Dictionary mit detaillierten Informationen zur Prüfungsleistung
        """
        return {
            "art": self.art,
            "datum": self.datum,
            "beschreibung": self.beschreibung,
            "deadline": self.deadline,
            "versuche": self.versuche,
            "anmerkung": self.anmerkung,
            "note": self.note.wert if self.note else None,
            "bestanden": self.bestanden
        }

    def get_deadline_in_days(self) -> int:
        """
        Berechnet die Anzahl der verbleibenden Tage bis zur Deadline.

        Nützlich für die Anzeige von Countdowns oder für die Priorisierung von
        bevorstehenden Abgaben.

        Rückgabe:
            Anzahl der Tage bis zur Deadline, oder 0 wenn keine Deadline vorhanden
            oder die Deadline bereits überschritten ist
        """
        if not self.deadline:
            return 0
        delta = self.deadline - date.today()
        return max(0, delta.days)  # Nie negative Tage zurückgeben

    def berechne_gesamtnote(self) -> float:
        """
        Gibt die Gesamtnote für diese Prüfungsleistung zurück.

        Diese Methode ist ein Wrapper für den Zugriff auf die Note, berücksichtigt
        aber auch den Fall, dass noch keine Note gesetzt wurde.

        Rückgabe:
            Der Notenwert oder 0.0, wenn keine Note vorhanden ist
        """
        return self.note.wert if self.note else 0.0

    def is_passed(self) -> bool:
        """
        Überprüft, ob die Prüfung bestanden wurde.

        Rückgabe:
            True, wenn die Prüfung bestanden wurde, False sonst
        """
        return self.bestanden

    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiert das Pruefungsleistung-Objekt in ein Dictionary zur Serialisierung.

        Diese Methode ist wichtig für die Persistenz der Daten, z.B. wenn sie
        in einer JSON-Datei gespeichert werden sollen.

        Rückgabe:
            Ein Dictionary mit den Attributen der Prüfungsleistung
        """
        return {
            "art": self.art,
            "datum": self.datum.isoformat() if self.datum else None,
            "beschreibung": self.beschreibung,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "versuche": self.versuche,
            "anmerkung": self.anmerkung,
            "note": self.note.to_dict() if self.note else None,
            "bestanden": self.bestanden
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pruefungsleistung':
        """
        Erstellt ein Pruefungsleistung-Objekt aus einem Dictionary.

        Diese Klassenmethode ist das Gegenstück zu to_dict() und ermöglicht die
        Deserialisierung von gespeicherten Prüfungsdaten.

        Parameter:
            data: Ein Dictionary mit den Attributen einer Prüfungsleistung

        Rückgabe:
            Ein neues Pruefungsleistung-Objekt, initialisiert mit den Daten aus dem Dictionary
        """
        pruefung = cls(
            art=data["art"],
            datum=date.fromisoformat(data["datum"]) if data.get("datum") else None,
            beschreibung=data.get("beschreibung", ""),
            deadline=date.fromisoformat(data["deadline"]) if data.get("deadline") else None,
            versuche=data.get("versuche", 1),
            anmerkung=data.get("anmerkung", "")
        )
        if data.get("note"):
            pruefung.note = Note.from_dict(data["note"])
            pruefung.bestanden = data.get("bestanden", False)
        return pruefung
