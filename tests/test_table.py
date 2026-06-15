import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.db.backend.table import Table
from src.db.backend.errors import MissingColumnError, UnknownColumnError


class TestTable(unittest.TestCase):
    def test_insert_record_success(self):
        table = Table(("id", "name"))
        table.insert_record({"id": 1, "name": "John"})
        self.assertEqual(len(table.records), 1)

    def test_insert_record_missing_column(self):
        table = Table(("id", "name"))
        with self.assertRaises(MissingColumnError):
            table.insert_record({"id": 1})

    def test_insert_record_extra_column(self):
        table = Table(("id", "name"))
        with self.assertRaises(UnknownColumnError):
            table.insert_record({"id": 1, "name": "John", "age": 20})

    def test_select_records_no_filters(self):
        table = Table(("id", "name"))
        table.insert_record({"id": 1, "name": "John"})
        records = table.select_records()
        self.assertEqual(len(records), 1)

    def test_select_records_with_filters(self):
        table = Table(("id", "name"))
        table.insert_record({"id": 1, "name": "John"})
        table.insert_record({"id": 2, "name": "Jane"})
        
        records = table.select_records(name="Jane")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], 2)

    def test_select_records_unknown_filter(self):
        table = Table(("id", "name"))
        with self.assertRaises(UnknownColumnError):
            table.select_records(age=20)

    def test_update_record_success(self):
        table = Table(("student_id", "name", "age"))
        table.insert_record({"student_id": 1, "name": "John", "age": 20})
        
        result = table.update_record(student_id=1, age=21)
        self.assertTrue(result)
        self.assertEqual(table.records[0]["age"], 21)

    def test_update_record_not_found(self):
        table = Table(("student_id", "name"))
        table.insert_record({"student_id": 1, "name": "John"})
        
        result = table.update_record(student_id=999, name="None")
        self.assertFalse(result)

    def test_delete_record_success(self):
        table = Table(("student_id", "name"))
        table.insert_record({"student_id": 1, "name": "John"})
        table.insert_record({"student_id": 2, "name": "Jane"})
        
        result = table.delete_record(1)
        self.assertTrue(result)
        self.assertEqual(len(table.records), 1)

    def test_delete_record_not_found(self):
        table = Table(("student_id", "name"))
        table.insert_record({"student_id": 1, "name": "John"})
        
        result = table.delete_record(999)
        self.assertFalse(result)

    def test_init_with_records(self):
        records = [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]
        table = Table(("id", "name"), records)
        self.assertEqual(len(table.records), 2)

    def test_sort_records(self):
        table = Table(("student_id", "name", "age"))
        table.insert_record({"student_id": 3, "name": "John", "age": 20})
        table.insert_record({"student_id": 1, "name": "Alice", "age": 22})
        table.insert_record({"student_id": 2, "name": "Bob", "age": 21})
        
        sorted_records = table.sort_records("student_id", reverse=False)
        
        self.assertEqual(sorted_records[0]["student_id"], 1)
        self.assertEqual(sorted_records[1]["student_id"], 2)
        self.assertEqual(sorted_records[2]["student_id"], 3)

    def test_get_all(self):
        table = Table(("id", "name"))
        table.insert_record({"id": 1, "name": "John"})
        
        all_records = table.get_all()
        self.assertEqual(len(all_records), 1)
        all_records.append({"id": 2, "name": "Jane"})
        self.assertEqual(len(table.records), 1)


if __name__ == "__main__":
    unittest.main()