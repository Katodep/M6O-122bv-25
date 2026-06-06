import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.db.backend.memory import MemoryDatabase
from src.db.backend.errors import TableNotFoundError, TableAlreadyExistsError


class TestMemoryDatabase(unittest.TestCase):
    def setUp(self):
        self.db = MemoryDatabase()

    def test_create_table(self):
        self.db.create_table("students", ("id", "name"))
        self.assertTrue(self.db._table_exists("students"))

    def test_create_table_already_exists(self):
        self.db.create_table("students", ("id", "name"))
        with self.assertRaises(TableAlreadyExistsError):
            self.db.create_table("students", ("id", "name"))

    def test_insert_record(self):
        self.db.create_table("students", ("id", "name"))
        self.db.insert_record("students", {"id": 1, "name": "Иван"})
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Иван")

    def test_select_with_filters(self):
        self.db.create_table("students", ("id", "name"))
        self.db.insert_record("students", {"id": 1, "name": "Иван"})
        self.db.insert_record("students", {"id": 2, "name": "Мария"})

        records = self.db.select_records("students", name="Мария")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], 2)

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

    def test_update_record_not_found(self):
        self.db.create_table("students", ("student_id", "name"))
        self.db.insert_record("students", {"student_id": 1, "name": "Иван"})
        
        result = self.db.update_record("students", student_id=999, name="None")
        self.assertFalse(result)

    def test_delete_record(self):
        self.db.create_table("students", ("student_id", "name"))
        self.db.insert_record("students", {"student_id": 1, "name": "Иван"})
        self.db.insert_record("students", {"student_id": 2, "name": "Мария"})
        
        result = self.db.delete_record("students", 1)
        self.assertTrue(result)
        
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["student_id"], 2)

    def test_delete_record_not_found(self):
        self.db.create_table("students", ("student_id", "name"))
        self.db.insert_record("students", {"student_id": 1, "name": "Иван"})
        
        result = self.db.delete_record("students", 999)
        self.assertFalse(result)

    def test_select_records(self):
        self.db.create_table("students", ("student_id", "name"))
        self.db.insert_record("students", {"student_id": 1, "name": "John"})
        
        records = self.db.select_records("students")
        self.assertEqual(len(records), 1)

    def test_select_record_with_filters(self):
        self.db.create_table("students", ("student_id", "name", "age"))
        self.db.insert_record("students", {"student_id": 1, "name": "John", "age": 20})
        self.db.insert_record("students", {"student_id": 2, "name": "Jane", "age": 25})
        
        records = self.db.select_records("students", age=25)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Jane")

    def test_select_record_no_filters(self):
        self.db.create_table("students", ("student_id", "name"))
        self.db.insert_record("students", {"student_id": 1, "name": "John"})
        self.db.insert_record("students", {"student_id": 2, "name": "Jane"})
        
        records = self.db.select_records("students")
        self.assertEqual(len(records), 2)

    def test_insert_record_missing_column(self):
        self.db.create_table("students", ("student_id", "name"))
        
        with self.assertRaises(Exception):
            self.db.insert_record("students", {"student_id": 1})

    def test_insert_record_extra_column(self):
        self.db.create_table("students", ("student_id", "name"))
        
        with self.assertRaises(Exception):
            self.db.insert_record("students", {"student_id": 1, "name": "John", "age": 20})


if __name__ == "__main__":
    unittest.main()