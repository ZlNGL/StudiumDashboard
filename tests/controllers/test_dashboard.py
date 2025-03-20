# tests/controllers/test_dashboard.py
import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock
from controllers import Dashboard, DatenManager
from models import Student, Studiengang, Semester, Modul, Pruefungsleistung, Note


class TestDashboard(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.daten_manager = MagicMock(spec=DatenManager)
        self.dashboard = Dashboard(self.daten_manager)

        # Create test student
        self.student = Student(
            vorname="Test",
            nachname="Student",
            geburtsdatum=date(2000, 1, 1),
            matrikelNr="123456",
            zielNotendurchschnitt=2.0
        )

        # Create test studiengang with modules
        self.studiengang = Studiengang(name="Test Degree", gesamtECTS=180)
        self.semester = Semester(nummer=1)
        self.studiengang.add_semester(self.semester)

        # Create module with exam
        self.modul = Modul(modulName="Test Module", modulID="TM1", ects=5)
        self.semester.add_modul(self.modul)

        self.pruefung = Pruefungsleistung(art="Klausur", datum=date.today())
        note = Note(typ="Note", wert=1.7, gewichtung=1.0)
        self.pruefung.set_note(note)
        self.modul.add_pruefungsleistung(self.pruefung)
        self.student.add_pruefungsleistung(self.pruefung)

        # Set up dashboard
        self.dashboard.student = self.student
        self.dashboard.studiengang = self.studiengang

    def test_berechne_notendurchschnitt(self):
        """Test grade average calculation."""
        self.assertEqual(self.dashboard.berechne_notendurchschnitt(), 1.7)

    def test_berechne_notendurchschnitt_no_student(self):
        """Test grade calculation safely handles missing student."""
        self.dashboard.student = None
        self.assertEqual(self.dashboard.berechne_notendurchschnitt(), 0.0)

    def test_berechne_ects_fortschritt(self):
        """Test ECTS progress tracking."""
        # Update ECTS for student
        self.student.update_ects_for_modul(self.modul, True)

        # Check progress calculation
        fortschritt = self.dashboard.berechne_ects_fortschritt()
        self.assertEqual(fortschritt["absolut"], 5)
        self.assertEqual(fortschritt["gesamt"], 180)
        self.assertAlmostEqual(fortschritt["prozent"], 2.78, places=2)

    def test_berechne_ects_fortschritt_no_student(self):
        """Test ECTS calculation safely handles missing student or studiengang."""
        self.dashboard.student = None
        fortschritt = self.dashboard.berechne_ects_fortschritt()
        self.assertEqual(fortschritt["absolut"], 0)
        self.assertEqual(fortschritt["gesamt"], 0)
        self.assertEqual(fortschritt["prozent"], 0.0)

    def test_zeige_notenverteilung(self):
        """Test grade distribution calculation."""
        verteilung = self.dashboard.zeige_notenverteilung()
        self.assertEqual(verteilung, {"1.7": 1})

        # Add another grade
        pruefung2 = Pruefungsleistung(art="Hausarbeit")
        note2 = Note(typ="Note", wert=1.7, gewichtung=1.0)
        pruefung2.set_note(note2)
        self.student.add_pruefungsleistungen(pruefung2)

        verteilung = self.dashboard.zeige_notenverteilung()
        self.assertEqual(verteilung, {"1.7": 2})

    def test_anstehende_pruefungen(self):
        """Test upcoming exam detection."""
        # Add future exam
        future_date = date.today() + timedelta(days=10)
        future_pruefung = Pruefungsleistung(
            art="Hausarbeit",
            datum=future_date,
            beschreibung="Future exam"
        )
        self.modul.add_pruefungsleistung(future_pruefung)

        upcoming = self.dashboard.anstehende_pruefungen(30)
        self.assertEqual(len(upcoming), 1)
        self.assertEqual(upcoming[0].beschreibung, "Future exam")

        # Exams outside the time window should not be included
        far_future_date = date.today() + timedelta(days=60)
        far_future_pruefung = Pruefungsleistung(
            art="Referat",
            datum=far_future_date,
            beschreibung="Far future exam"
        )
        self.modul.add_pruefungsleistung(far_future_pruefung)

        upcoming = self.dashboard.anstehende_pruefungen(30)
        self.assertEqual(len(upcoming), 1)  # Still only one

    def test_zeige_semesterdurchschnitte(self):
        """Test semester average grade calculation."""
        semester_noten = self.dashboard.zeige_semesterdurchschnitte()
        self.assertEqual(semester_noten, {1: 1.7})

        # Add another semester with a different grade
        semester2 = Semester(nummer=2)
        self.studiengang.add_semester(semester2)

        modul2 = Modul(modulName="Test Module 2", modulID="TM2", ects=5)
        semester2.add_modul(modul2)

        pruefung2 = Pruefungsleistung(art="Klausur")
        note2 = Note(typ="Note", wert=2.3, gewichtung=1.0)
        pruefung2.set_note(note2)
        modul2.add_pruefungsleistung(pruefung2)
        self.student.add_pruefungsleistung(pruefung2)

        semester_noten = self.dashboard.zeige_semesterdurchschnitte()
        self.assertEqual(semester_noten, {1: 1.7, 2: 2.3})

    def test_zeige_semesterdurchschnitte_weightings(self):
        """Test semester average calculation with different weightings."""
        # Add another exam to the same semester with different weighting
        pruefung2 = Pruefungsleistung(art="Hausarbeit")
        note2 = Note(typ="Note", wert=1.0, gewichtung=2.0)  # Double weight
        pruefung2.set_note(note2)
        self.modul.add_pruefungsleistung(pruefung2)
        self.student.add_pruefungsleistung(pruefung2)

        # Expected: (1.7*1.0 + 1.0*2.0)/(1.0+2.0) = 1.23
        expected = round((1.7 * 1.0 + 1.0 * 2.0) / (1.0 + 2.0), 2)

        semester_noten = self.dashboard.zeige_semesterdurchschnitte()
        self.assertEqual(semester_noten, {1: expected})

    def test_zeige_semesterdurchschnitte_empty_semester(self):
        """Test semester average calculation handles empty semesters."""
        # Add empty semester
        empty_semester = Semester(nummer=3)
        self.studiengang.add_semester(empty_semester)

        semester_noten = self.dashboard.zeige_semesterdurchschnitte()
        self.assertEqual(semester_noten, {1: 1.7, 3: 0.0})

    def test_erfasse_note(self):
        """Test adding a new grade."""
        # Set up mock for saving
        self.daten_manager.speichern.return_value = True

        # Create a new module
        new_modul = Modul(modulName="New Module", modulID="NM1", ects=5)
        self.semester.add_modul(new_modul)

        # Create grade data
        pruefung_data = {
            "art": "Hausarbeit",
            "datum": date.today(),
            "beschreibung": "Test grade",
            "typ": "Note",
            "wert": 2.0,
            "gewichtung": 1.0
        }

        # Add grade
        result = self.dashboard.erfasse_note("New Module", pruefung_data)
        self.assertTrue(result)

        # Verify new grade was added
        self.assertEqual(len(self.student.pruefungsleistungen), 2)
        self.assertEqual(len(new_modul.pruefungsleistungen), 1)

        # Verify datenmanager.speichern was called
        self.daten_manager.speichern.assert_called_once()

    def test_erfasse_note_modul_not_found(self):
        """Test adding a grade to a non-existent module."""
        pruefung_data = {
            "art": "Hausarbeit",
            "datum": date.today(),
            "beschreibung": "Test grade",
            "typ": "Note",
            "wert": 2.0,
            "gewichtung": 1.0
        }

        # Try to add grade to non-existent module
        result = self.dashboard.erfasse_note("Non-existent Module", pruefung_data)
        self.assertFalse(result)

        # Verify no grade was added
        self.assertEqual(len(self.student.pruefungsleistungen), 1)

    def test_error_handling(self):
        """Test error handling mechanism."""
        # Create scenario that will cause error
        self.student.get_durchschnittnote = MagicMock(side_effect=ValueError("Test error"))

        # Call method that should handle the error
        result = self.dashboard.berechne_notendurchschnitt()

        # Verify error was handled and proper fallback value returned
        self.assertEqual(result, 0.0)


if __name__ == '__main__':
    unittest.main()