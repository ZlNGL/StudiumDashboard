# tests/controllers/test_datenmanager.py
import unittest
import os
import tempfile
import json
import csv
from datetime import date
from unittest.mock import patch, mock_open
from controllers.datenmanager import DatenManager
from models import Student, Studiengang, Semester, Modul, Pruefungsleistung, Note


class TestDatenManager(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary file for tests
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = os.path.join(self.temp_dir, "test_data.json")
        self.csv_file = os.path.join(self.temp_dir, "test_export.csv")

        # Create DatenManager with temp file
        self.daten_manager = DatenManager(self.temp_file)

        # Create test objects
        self.student = Student(
            vorname="Test",
            nachname="Student",
            geburtsdatum=date(2000, 1, 1),
            matrikelNr="123456",
            zielNotendurchschnitt=2.0
        )

        self.studiengang = Studiengang(name="Test Degree", gesamtECTS=180)
        semester = Semester(nummer=1)
        self.studiengang.add_semester(semester)

        modul = Modul(modulName="Test Module", modulID="TM1", ects=5)
        semester.add_modul(modul)

        pruefung = Pruefungsleistung(art="Klausur", datum=date.today())
        note = Note(typ="Note", wert=1.7, gewichtung=1.0)
        pruefung.set_note(note)
        modul.add_pruefungsleistung(pruefung)
        self.student.add_pruefungsleistung(pruefung)

    def tearDown(self):
        """Clean up after tests."""
        # Remove temp files
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)
        os.rmdir(self.temp_dir)

    def test_speichern_laden(self):
        """Test saving and loading data."""
        # Save data
        result = self.daten_manager.speichern(self.studiengang, self.student)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.temp_file))

        # Load data
        loaded_studiengang, loaded_student = self.daten_manager.laden()

        # Check loaded data
        self.assertIsNotNone(loaded_studiengang)
        self.assertIsNotNone(loaded_student)
        self.assertEqual(loaded_studiengang.name, "Test Degree")
        self.assertEqual(loaded_student.vorname, "Test")
        self.assertEqual(loaded_student.nachname, "Student")

    def test_speichern_missing_data(self):
        """Test saving with missing data."""
        result = self.daten_manager.speichern(None, self.student)
        self.assertFalse(result)

        result = self.daten_manager.speichern(self.studiengang, None)
        self.assertFalse(result)

    def test_laden_nonexistent_file(self):
        """Test loading from a non-existent file."""
        # Use a non-existent file
        manager = DatenManager("nonexistent_file.json")
        studiengang, student = manager.laden()

        self.assertIsNone(studiengang)
        self.assertIsNone(student)

    def test_laden_invalid_json(self):
        """Test loading from an invalid JSON file."""
        # Create invalid JSON file
        with open(self.temp_file, 'w') as f:
            f.write("This is not valid JSON")

        studiengang, student = self.daten_manager.laden()

        self.assertIsNone(studiengang)
        self.assertIsNone(student)

    def test_laden_missing_keys(self):
        """Test loading from JSON with missing keys."""
        # Create JSON with missing keys
        with open(self.temp_file, 'w') as f:
            json.dump({"some_key": "some_value"}, f)

        studiengang, student = self.daten_manager.laden()

        self.assertIsNone(studiengang)
        self.assertIsNone(student)

    def test_export_csv(self):
        """Test exporting data to CSV."""
        result = self.daten_manager.export_csv(self.student, self.studiengang, self.csv_file)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.csv_file))

        # Check CSV content
        with open(self.csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            row = next(reader)

            self.assertIn("Modul_ID", header)
            self.assertIn("Modul_Name", header)
            self.assertIn("Note", header)

            self.assertIn("Test Module", row)  # Module name should be in the row
            self.assertIn("1.7", row)  # Note value should be in the row

    def test_validate_csv_row(self):
        """Test CSV row validation."""
        # Valid row
        valid_row = {
            "Prüfungsart": "Klausur",
            "Datum": date.today().isoformat(),
            "Note": "1.7",
            "Gewichtung": "1.0"
        }
        issues = self.daten_manager.validate_csv_row(valid_row)
        self.assertEqual(issues, [])

        # Invalid row - missing required field
        invalid_row1 = {
            "Datum": date.today().isoformat(),
            "Note": "1.7"
        }
        issues = self.daten_manager.validate_csv_row(invalid_row1)
        self.assertGreater(len(issues), 0)

        # Invalid row - invalid note value
        invalid_row2 = {
            "Prüfungsart": "Klausur",
            "Datum": date.today().isoformat(),
            "Note": "invalid"
        }
        issues = self.daten_manager.validate_csv_row(invalid_row2)
        self.assertGreater(len(issues), 0)

        # Invalid row - out of range note value
        invalid_row3 = {
            "Prüfungsart": "Klausur",
            "Datum": date.today().isoformat(),
            "Note": "6.0"
        }
        issues = self.daten_manager.validate_csv_row(invalid_row3)
        self.assertGreater(len(issues), 0)

        # Invalid row - invalid date
        invalid_row4 = {
            "Prüfungsart": "Klausur",
            "Datum": "invalid-date",
            "Note": "1.7"
        }
        issues = self.daten_manager.validate_csv_row(invalid_row4)
        self.assertGreater(len(issues), 0)

    @patch('builtins.open', new_callable=mock_open,
           read_data='Modul_ID,Modul_Name,Prüfungsart,Datum,Beschreibung,Note,Gewichtung,Bestanden\n,Test Module,Klausur,2023-01-01,Test,1.7,1.0,Ja')
    def test_import_csv(self, mock_file):
        """Test importing data from CSV."""
        # Mock os.path.exists to return True
        with patch('os.path.exists', return_value=True):
            result = self.daten_manager.import_csv(self.student, self.studiengang, "mock_import.csv")
            self.assertTrue(result)

    def test_import_csv_nonexistent_file(self):
        """Test importing from a non-existent file."""
        result = self.daten_manager.import_csv(self.student, self.studiengang, "nonexistent_file.csv")
        self.assertFalse(result)

    @patch('builtins.open', new_callable=mock_open, read_data='Invalid,CSV,Format')
    def test_import_csv_invalid_format(self, mock_file):
        """Test importing from a CSV with invalid format."""
        # Mock os.path.exists to return True
        with patch('os.path.exists', return_value=True):
            result = self.daten_manager.import_csv(self.student, self.studiengang, "invalid_format.csv")
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()