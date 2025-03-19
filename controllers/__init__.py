# controllers/__init__.py
# Diese Datei ermöglicht einen einfacheren Zugriff auf die Controller-Klassen
# von außerhalb des Pakets. Das fördert eine saubere Codestruktur und erhöht
# die Lesbarkeit bei Importen in anderen Teilen der Anwendung.

from .datenmanager import DatenManager
from .dashboard import Dashboard