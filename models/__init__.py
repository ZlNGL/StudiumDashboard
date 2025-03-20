# models/__init__.py
# Diese Datei importiert alle Modelklassen, damit diese einfach von außerhalb des Pakets
# importiert werden können. Dies folgt dem Prinzip der einfachen Importierbarkeit von
# Modulen und erhöht die Lesbarkeit des Codes an anderen Stellen im Projekt.

# Verbesserte Importstruktur zur Vermeidung zirkulärer Importe
from .base_model import BaseModel
from .person import Person
from .note import Note
from .pruefungsleistung import Pruefungsleistung
from .modul import Modul
from .semester import Semester
from .student import Student
from .studiengang import Studiengang