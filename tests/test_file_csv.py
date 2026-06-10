import tempfile
import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.db.backend.file_csv import CSVDatabase
from src.db.backend.errors import TableNotFoundError


class TestCSVDatabase(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db = CSVDatabase(self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_table(self):
        self.db.create_table("students", ("student_id", "name", "age"))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "students.csv")))

    def test_insert_and_select(self):
        self.db.create_table("students", ("student_id", "name", "age"))
        self.db.insert_record("students", {"student_id": 1, "name": "Иван", "age": 20})
        
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Иван")

    def test_select_with_filters(self):
        self.db.create_table("students", ("student_id", "name"))
        self.db.insert_record("students", {"student_id": 1, "name": "Иван"})
        self.db.insert_record("students", {"student_id": 2, "name": "Мария"})

        records = self.db.select_records("students", name="Мария")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["student_id"], 2)

    def test_select_from_missing_table(self):
        with self.assertRaises(TableNotFoundError):
            self.db.select_records("nonexistent")

    def test_update_record(self):
        self.db.create_table("students", ("student_id", "name", "age"))
        self.db.insert_record("students", {"student_id": 1, "name": "Иван", "age": 20})
        
        result = self.db.update_record("students", student_id=1, age=21)
        self.assertTrue(result)
        
        records = self.db.select_records("students", student_id=1)
        self.assertEqual(records[0]["age"], 21)

    def test_delete_record(self):
        self.db.create_table("students", ("student_id", "name"))
        self.db.insert_record("students", {"student_id": 1, "name": "Иван"})
        self.db.insert_record("students", {"student_id": 2, "name": "Мария"})
        
        result = self.db.delete_record("students", 1)
        self.assertTrue(result)
        
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["student_id"], 2)


if __name__ == "__main__":
    unittest.main()