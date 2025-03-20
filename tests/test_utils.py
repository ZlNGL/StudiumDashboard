# tests/test_utils.py
"""
Utility functions and fixtures for tests.

This module contains helper functions and common fixtures
that can be reused across different test modules.
"""

import os
import tempfile
from datetime import date
from models import Student, Studiengang, Semester, Modul, Pruefungsleistung, Note


def create_temp_file():
    """Create a temporary file and return its path."""
    fd, path = tempfile.mkstemp()
    os.close(fd)
    return path


def create_test_data():
    """Create a complete set of test data objects."""
    # Create student
    student = Student(
        vorname="Test",
        nachname="Student",
        geburtsdatum=date(2000, 1, 1),
        matrikelNr="123456",
        email="test@example.com",
        zielNotendurchschnitt=2.0
    )

    # Create studiengang
    studiengang = Studiengang(name="Test Degree", gesamtECTS=180)

    # Create first semester with modules
    semester1 = Semester(nummer=1)
    studiengang.add_semester(semester1)

    modul1 = Modul(modulName="Module 1.1", modulID="M11", ects=5, semesterZuordnung=1)
    modul2 = Modul(modulName="Module 1.2", modulID="M12", ects=10, semesterZuordnung=1)

    semester1.add_modul(modul1)
    semester1.add_modul(modul2)

    # Create second semester with modules
    semester2 = Semester(nummer=2)
    studiengang.add_semester(semester2)

    modul3 = Modul(modulName="Module 2.1", modulID="M21", ects=5, semesterZuordnung=2)
    semester2.add_modul(modul3)

    # Create exams and grades
    pruefung1 = Pruefungsleistung(art="Klausur", datum=date(2023, 1, 15))
    note1 = Note(typ="Note", wert=1.3, gewichtung=1.0)
    pruefung1.set_note(note1)

    pruefung2 = Pruefungsleistung(art="Hausarbeit", datum=date(2023, 2, 20))
    note2 = Note(typ="Note", wert=2.0, gewichtung=1.0)
    pruefung2.set_note(note2)

    pruefung3 = Pruefungsleistung(art="Klausur", datum=date(2023, 7, 10))
    note3 = Note(typ="Note", wert=1.7, gewichtung=1.0)
    pruefung3.set_note(note3)

    # Add exams to modules
    modul1.add_pruefungsleistung(pruefung1)
    modul2.add_pruefungsleistung(pruefung2)
    modul3.add_pruefungsleistung(pruefung3)

    # Add exams to student
    student.add_pruefungsleistung(pruefung1)
    student.add_pruefungsleistung(pruefung2)
    student.add_pruefungsleistung(pruefung3)

    # Add passed modules to student's ECTS
    student.update_ects_for_modul(modul1, True)
    student.update_ects_for_modul(modul2, True)
    student.update_ects_for_modul(modul3, True)

    return student, studiengang


def create_sample_pruefung(art="Klausur", wert=1.7, bestanden=True):
    """Create a sample exam with the given parameters."""
    pruefung = Pruefungsleistung(art=art, datum=date.today())
    if wert is not None:
        note = Note(typ=art, wert=wert, gewichtung=1.0)
        pruefung.set_note(note)
        pruefung.bestanden = bestanden
    return pruefung


def create_sample_csv_row(modul_id="M1", modul_name="Test Module",
                          pruefungsart="Klausur", datum=None,
                          beschreibung="Test exam", note=1.7,
                          gewichtung=1.0, bestanden="Ja"):
    """Create a sample CSV row for testing import/export."""
    if datum is None:
        datum = date.today().isoformat()

    return {
        "Modul_ID": modul_id,
        "Modul_Name": modul_name,
        "Prüfungsart": pruefungsart,
        "Datum": datum,
        "Beschreibung": beschreibung,
        "Note": str(note),
        "Gewichtung": str(gewichtung),
        "Bestanden": bestanden
    }