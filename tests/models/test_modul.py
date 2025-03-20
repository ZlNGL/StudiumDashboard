# tests/models/test_modul.py
import unittest
from datetime import date
from models import Modul, Pruefungsleistung, Note, Student


class TestModul(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.modul = Modul(
            modulName="Test Module",
            modulID="TM1",
            beschreibung="A test module",
            ects=5,
            semesterZuordnung=1
        )

        self.student = Student(
            vorname="Test",
            nachname="Student",
            geburtsdatum=date(2000, 1, 1),
            matrikelNr="123456"
        )

    def test_default_attributes(self):
        """Test default attribute values."""
        self.assertEqual(self.modul.modulName, "Test Module")
        self.assertEqual(self.modul.modulID, "TM1")
        self.assertEqual(self.modul.beschreibung, "A test module")
        self.assertEqual(self.modul.ects, 5)
        self.assertEqual(self.modul.semesterZuordnung, 1)
        self.assertEqual(self.modul.pruefungsleistungen, [])
        self.assertEqual(self.modul.required_for_completion, [])

    def test_get_ects(self):
        """Test get_ects method returns correct value."""
        self.assertEqual(self.modul.get_ects(), 5)

        # Change ECTS value
        self.modul.ects = 10
        self.assertEqual(self.modul.get_ects(), 10)

    def test_get_name(self):
        """Test get_name method returns correct value."""
        self.assertEqual(self.modul.get_name(), "Test Module")

        # Change module name
        self.modul.modulName = "New Name"
        self.assertEqual(self.modul.get_name(), "New Name")

    def test_is_complete_no_exams(self):
        """Test module is not complete when there are no exams."""
        self.assertFalse(self.modul.is_complete_for_student(self.student))

    def test_is_complete_with_passed_exam(self):
        """Test module is complete when at least one exam is passed."""
        # Add a passed exam
        pruefung = Pruefungsleistung(art="Klausur")
        note = Note(typ="Note", wert=1.7, gewichtung=1.0)
        pruefung.set_note(note)
        self.modul.add_pruefungsleistung(pruefung)

        self.assertTrue(self.modul.is_complete_for_student(self.student))

    def test_is_complete_with_failed_exam(self):
        """Test module is not complete when exam is failed."""
        # Add a failed exam
        pruefung = Pruefungsleistung(art="Klausur")
        note = Note(typ="Note", wert=5.0, gewichtung=1.0)  # Failed in German system
        pruefung.set_note(note)
        pruefung.bestanden = False
        self.modul.add_pruefungsleistung(pruefung)

        self.assertFalse(self.modul.is_complete_for_student(self.student))

    def test_is_complete_with_required_exams(self):
        """Test module completion with specific required exams."""
        # Set required exam types
        self.modul.required_for_completion = ["Klausur", "Hausarbeit"]

        # Add a passed exam of one type
        pruefung1 = Pruefungsleistung(art="Klausur")
        note1 = Note(typ="Note", wert=1.7, gewichtung=1.0)
        pruefung1.set_note(note1)
        self.modul.add_pruefungsleistung(pruefung1)

        # Module should not be complete yet (missing Hausarbeit)
        self.assertFalse(self.modul.is_complete_for_student(self.student))

        # Add second required exam
        pruefung2 = Pruefungsleistung(art="Hausarbeit")
        note2 = Note(typ="Note", wert=2.0, gewichtung=1.0)
        pruefung2.set_note(note2)
        self.modul.add_pruefungsleistung(pruefung2)

        # Now module should be complete
        self.assertTrue(self.modul.is_complete_for_student(self.student))

    def test_add_pruefungsleistung(self):
        """Test adding a Pruefungsleistung to a module."""
        pruefung = Pruefungsleistung(art="Klausur")
        self.modul.add_pruefungsleistung(pruefung)

        self.assertEqual(len(self.modul.pruefungsleistungen), 1)
        self.assertEqual(self.modul.pruefungsleistungen[0], pruefung)
        self.assertEqual(pruefung.modul_id, self.modul.id)

    def test_add_pruefungsleistung_wrong_type(self):
        """Test adding wrong type raises TypeError."""
        with self.assertRaises(TypeError):
            self.modul.add_pruefungsleistung("Not a Pruefungsleistung")

    def test_get_current_grade_no_exams(self):
        """Test grade calculation with no exams."""
        self.assertEqual(self.modul.get_current_grade(), 0.0)

    def test_get_current_grade_with_exams(self):
        """Test grade calculation with passed exams."""
        # Add a passed exam
        pruefung = Pruefungsleistung(art="Klausur")
        note = Note(typ="Note", wert=1.7, gewichtung=1.0)
        pruefung.set_note(note)
        self.modul.add_pruefungsleistung(pruefung)

        self.assertEqual(self.modul.get_current_grade(), 1.7)

    def test_get_current_grade_weighted(self):
        """Test weighted grade calculation."""
        # Add exams with different weights
        pruefung1 = Pruefungsleistung(art="Klausur")
        note1 = Note(typ="Note", wert=1.7, gewichtung=1.0)
        pruefung1.set_note(note1)
        self.modul.add_pruefungsleistung(pruefung1)

        pruefung2 = Pruefungsleistung(art="Hausarbeit")
        note2 = Note(typ="Note", wert=2.3, gewichtung=2.0)
        pruefung2.set_note(note2)
        self.modul.add_pruefungsleistung(pruefung2)

        # Expected calculation: (1.7*1.0 + 2.3*2.0)/(1.0+2.0) = 2.1
        expected = (1.7 * 1.0 + 2.3 * 2.0) / (1.0 + 2.0)
        self.assertAlmostEqual(self.modul.get_current_grade(), expected, places=2)

    def test_get_current_grade_only_passed(self):
        """Test grade calculation only includes passed exams."""
        # Add a passed exam
        pruefung1 = Pruefungsleistung(art="Klausur")
        note1 = Note(typ="Note", wert=1.7, gewichtung=1.0)
        pruefung1.set_note(note1)
        self.modul.add_pruefungsleistung(pruefung1)

        # Add a failed exam
        pruefung2 = Pruefungsleistung(art="Hausarbeit")
        note2 = Note(typ="Note", wert=5.0, gewichtung=1.0)
        pruefung2.set_note(note2)
        pruefung2.bestanden = False
        self.modul.add_pruefungsleistung(pruefung2)

        # Only the passed exam should be counted
        self.assertEqual(self.modul.get_current_grade(), 1.7)

    def test_to_dict(self):
        """Test serialization to dictionary."""
        # Add exam to the module
        pruefung = Pruefungsleistung(art="Klausur")
        note = Note(typ="Note", wert=1.7, gewichtung=1.0)
        pruefung.set_note(note)
        self.modul.add_pruefungsleistung(pruefung)

        # Serialize
        data = self.modul.to_dict()

        # Check serialized data
        self.assertEqual(data["modulName"], "Test Module")
        self.assertEqual(data["modulID"], "TM1")
        self.assertEqual(data["beschreibung"], "A test module")
        self.assertEqual(data["ects"], 5)
        self.assertEqual(data["semesterZuordnung"], 1)
        self.assertEqual(len(data["pruefungsleistungen"]), 1)
        self.assertEqual(data["required_for_completion"], [])

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        # Create dictionary representation
        data = {
            "id": "test-id",
            "modulName": "From Dict Module",
            "modulID": "FDM1",
            "beschreibung": "Created from dictionary",
            "ects": 10,
            "semesterZuordnung": 2,
            "required_for_completion": ["Klausur"],
            "pruefungsleistungen": [
                {
                    "id": "pl-id",
                    "art": "Klausur",
                    "datum": date.today().isoformat(),
                    "beschreibung": "Test exam",
                    "note": {
                        "id": "note-id",
                        "typ": "Note",
                        "wert": 2.0,
                        "gewichtung": 1.0,
                        "datum": date.today().isoformat(),
                        "kommentar": "",
                        "punkte": 0
                    },
                    "bestanden": True
                }
            ]
        }

        # Deserialize
        modul = Modul.from_dict(data)

        # Check deserialized object
        self.assertEqual(modul.id, "test-id")
        self.assertEqual(modul.modulName, "From Dict Module")
        self.assertEqual(modul.modulID, "FDM1")
        self.assertEqual(modul.beschreibung, "Created from dictionary")
        self.assertEqual(modul.ects, 10)
        self.assertEqual(modul.semesterZuordnung, 2)
        self.assertEqual(modul.required_for_completion, ["Klausur"])
        self.assertEqual(len(modul.pruefungsleistungen), 1)
        self.assertEqual(modul.pruefungsleistungen[0].art, "Klausur")
        self.assertEqual(modul.pruefungsleistungen[0].note.wert, 2.0)


if __name__ == '__main__':
    unittest.main()