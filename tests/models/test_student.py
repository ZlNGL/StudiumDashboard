# tests/models/test_student.py
import unittest
from datetime import date
from models import Student, Pruefungsleistung, Note, Modul


class TestStudent(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.student = Student(
            vorname="Test",
            nachname="Student",
            geburtsdatum=date(2000, 1, 1),
            matrikelNr="123456",
            email="test@example.com",
            zielNotendurchschnitt=2.0
        )

        self.modul1 = Modul(
            modulName="Test Module 1",
            modulID="TM1",
            ects=5,
            semesterZuordnung=1
        )

        self.pruefung1 = Pruefungsleistung(
            art="Klausur",
            datum=date.today(),
            beschreibung="Test Exam 1"
        )
        self.note1 = Note(typ="Note", wert=1.3, gewichtung=1.0)
        self.pruefung1.set_note(self.note1)
        self.pruefung1.modul_id = self.modul1.id

    def test_get_durchschnittnote_empty(self):
        """Test average grade calculation with no exams."""
        self.assertEqual(self.student.get_durchschnittnote(), 0.0)

    def test_get_durchschnittnote_single(self):
        """Test average grade calculation with one exam."""
        self.student.add_pruefungsleistung(self.pruefung1)
        self.assertEqual(self.student.get_durchschnittnote(), 1.3)

    def test_get_durchschnittnote_weighted(self):
        """Test weighted average grade calculation."""
        self.student.add_pruefungsleistung(self.pruefung1)

        # Add second exam with different weight
        pruefung2 = Pruefungsleistung(art="Hausarbeit")
        note2 = Note(typ="Note", wert=2.7, gewichtung=2.0)
        pruefung2.set_note(note2)
        self.student.add_pruefungsleistung(pruefung2)

        # Expected: (1.3*1.0 + 2.7*2.0)/(1.0+2.0) = 2.23
        expected = (1.3 * 1.0 + 2.7 * 2.0) / (1.0 + 2.0)
        self.assertAlmostEqual(self.student.get_durchschnittnote(), expected, places=2)

    def test_get_durchschnittnote_failed_excluded(self):
        """Test that failed exams are excluded from average calculation."""
        self.student.add_pruefungsleistung(self.pruefung1)

        # Add failed exam
        pruefung2 = Pruefungsleistung(art="Hausarbeit")
        note2 = Note(typ="Note", wert=5.0, gewichtung=1.0)  # Failed in German system
        pruefung2.set_note(note2)
        # This should mark the exam as not passed
        pruefung2.bestanden = False
        self.student.add_pruefungsleistung(pruefung2)

        # Only the first passed exam should be counted
        self.assertEqual(self.student.get_durchschnittnote(), 1.3)

    def test_get_durchschnittnote_no_weight(self):
        """Test average grade calculation with zero-weight exams."""
        # Add exam with zero weight
        pruefung = Pruefungsleistung(art="Test")
        note = Note(typ="Note", wert=1.0, gewichtung=0.0)
        pruefung.set_note(note)
        self.student.add_pruefungsleistung(pruefung)

        # Should handle division by zero gracefully
        self.assertEqual(self.student.get_durchschnittnote(), 0.0)

    def test_ects_tracking_add(self):
        """Test ECTS are correctly added when modules are passed."""
        self.assertEqual(self.student.absolvierteECTS, 0)

        # Add first module (5 ECTS)
        self.student.update_ects_for_modul(self.modul1, True)
        self.assertEqual(self.student.absolvierteECTS, 5)

        # Add second module (10 ECTS)
        modul2 = Modul(modulName="Test Module 2", modulID="TM2", ects=10)
        self.student.update_ects_for_modul(modul2, True)
        self.assertEqual(self.student.absolvierteECTS, 15)

    def test_ects_tracking_remove(self):
        """Test ECTS are correctly subtracted when modules are no longer passed."""
        # Add modules
        self.student.update_ects_for_modul(self.modul1, True)
        modul2 = Modul(modulName="Test Module 2", modulID="TM2", ects=10)
        self.student.update_ects_for_modul(modul2, True)
        self.assertEqual(self.student.absolvierteECTS, 15)

        # Remove first module
        self.student.update_ects_for_modul(self.modul1, False)
        self.assertEqual(self.student.absolvierteECTS, 10)

    def test_ects_tracking_duplicate(self):
        """Test ECTS are not double-counted when updating module status repeatedly."""
        self.assertEqual(self.student.absolvierteECTS, 0)

        # Add module once
        self.student.update_ects_for_modul(self.modul1, True)
        self.assertEqual(self.student.absolvierteECTS, 5)

        # Try to add the same module again
        self.student.update_ects_for_modul(self.modul1, True)
        self.assertEqual(self.student.absolvierteECTS, 5)  # Should still be 5

    def test_module_completion_tracking(self):
        """Test module completion tracking works correctly."""
        # Module should not be marked as passed initially
        self.assertFalse(self.student.hat_modul_bestanden(self.modul1))

        # Add module to passed list
        self.student.update_ects_for_modul(self.modul1, True)

        # Now module should be marked as passed
        self.assertTrue(self.student.hat_modul_bestanden(self.modul1))

    def test_serialization(self):
        """Test serialization to dictionary and back."""
        # Add some data
        self.student.add_pruefungsleistung(self.pruefung1)
        self.student.update_ects_for_modul(self.modul1, True)

        # Serialize to dict
        student_dict = self.student.to_dict()

        # Deserialize from dict
        restored_student = Student.from_dict(student_dict)

        # Check data is preserved
        self.assertEqual(restored_student.vorname, "Test")
        self.assertEqual(restored_student.nachname, "Student")
        self.assertEqual(restored_student.matrikelNr, "123456")
        self.assertEqual(restored_student.absolvierteECTS, 5)
        self.assertEqual(len(restored_student.pruefungsleistungen), 1)
        self.assertEqual(len(restored_student._bestandene_module_ids), 1)


if __name__ == '__main__':
    unittest.main()