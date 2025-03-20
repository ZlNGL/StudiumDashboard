# models/base_model.py
import uuid
from typing import Dict, Any


class BaseModel:
    """
    Basisklasse für alle Modelle mit gemeinsamen Funktionen wie ID-Generierung.
    Dient zur Vereinheitlichung der Modellklassen und zur Reduktion von Codewiederholung.
    """

    def __init__(self):
        """
        Initialisiert ein BaseModel-Objekt mit einer eindeutigen ID.
        """
        self.id = str(uuid.uuid4())  # Generiere eindeutige ID

    def to_dict(self) -> Dict[str, Any]:
        """
        Basisimplementierung für die Konvertierung in ein Dictionary.

        Rückgabe:
            Ein Dictionary mit der ID des Objekts
        """
        return {"id": self.id}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """
        Basisimplementierung für die Erstellung eines Objekts aus einem Dictionary.

        Parameter:
            data: Ein Dictionary mit den Attributen des Objekts

        Rückgabe:
            Eine neue Instanz der Klasse
        """
        instance = cls()
        if "id" in data:
            instance.id = data["id"]
        return instance