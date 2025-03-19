# models/__init__.py
# Diese Datei importiert alle Modelklassen, damit diese einfach von außerhalb des Pakets
# importiert werden können. Dies folgt dem Prinzip der einfachen Importierbarkeit von
# Modulen und erhöht die Lesbarkeit des Codes an anderen Stellen im Projekt.

from .person import Person
from .student import Student
from .note import Note
from .pruefungsleistung import Pruefungsleistung
from .modul import Modul
from .semester import Semester
from .studiengang import Studiengang