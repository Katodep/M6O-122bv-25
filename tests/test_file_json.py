import tempfile
import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.db.backend.file_json import JSONDatabase
from src.db.backend.errors import TableNotFoundError


class TestJSONDatabase(unittest.TestCase):
    def test_create_table(self):
        with tempfile.TemporaryDirectory() as directory:
            db = JSONDatabase(directory)
            db.create_table("students", ("student_id", "name", "age"))
            self.assertTrue(os.path.exists(os.path.join(directory, "students.json")))

    def test_data_persists_between_instances(self):
        with tempfile.TemporaryDirectory() as directory:
            first_db = JSONDatabase(directory)
            first_db.create_table("students", ("student_id", "name"))
            first_db.insert_record("students", {"student_id": 1, "name": "Иван"})

            second_db = JSONDatabase(directory)
            records = second_db.select_records("students")
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["name"], "Иван")

    def test_select_with_filters(self):
        with tempfile.TemporaryDirectory() as directory:
            db = JSONDatabase(directory)
            db.create_table("students", ("student_id", "name"))
            db.insert_record("students", {"student_id": 1, "name": "Иван"})
            db.insert_record("students", {"student_id": 2, "name": "Мария"})

            records = db.select_records("students", name="Мария")
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["student_id"], 2)

    def test_select_from_missing_table(self):
        with tempfile.TemporaryDirectory() as directory:
            db = JSONDatabase(directory)
            with self.assertRaises(TableNotFoundError):
                db.select_records("nonexistent")

    def test_update_record(self):
        with tempfile.TemporaryDirectory() as directory:
            db = JSONDatabase(directory)
            db.create_table("students", ("student_id", "name", "age"))
            db.insert_record("students", {"student_id": 1, "name": "Иван", "age": 20})
            
            result = db.update_record("students", student_id=1, age=21)
            self.assertTrue(result)
            
            records = db.select_records("students", student_id=1)
            self.assertEqual(records[0]["age"], 21)

    def test_delete_record(self):
        with tempfile.TemporaryDirectory() as directory:
            db = JSONDatabase(directory)
            db.create_table("students", ("student_id", "name"))
            db.insert_record("students", {"student_id": 1, "name": "Иван"})
            db.insert_record("students", {"student_id": 2, "name": "Мария"})
            
            result = db.delete_record("students", 1)
            self.assertTrue(result)
            
            records = db.select_records("students")
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["student_id"], 2)


if __name__ == "__main__":
    unittest.main()