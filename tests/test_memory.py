import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.db.backend.memory import StudentTable
from src.db.backend.errors import InvalidAgeError, DuplicateIDError


class TestStudentTable(unittest.TestCase):
    
    def setUp(self):
        self.table = StudentTable()
    
    def test_create_record_success(self):
        record = self.table.create_record(
            student_id=1,
            first_name="John",
            second_name="Doe",
            age=20,
            sex="M"
        )
        self.assertEqual(record["student_id"], 1)
        self.assertEqual(record["first_name"], "John")
        self.assertEqual(record["second_name"], "Doe")
        self.assertEqual(record["age"], 20)
        self.assertEqual(record["sex"], "M")
    
    def test_create_record_auto_id(self):
        record1 = self.table.create_record(first_name="John", second_name="Doe", age=20, sex="M")
        record2 = self.table.create_record(first_name="Jane", second_name="Smith", age=22, sex="F")
        
        self.assertEqual(record1["student_id"], 1)
        self.assertEqual(record2["student_id"], 2)
    
    def test_create_record_negative_age(self):
        with self.assertRaises(InvalidAgeError):
            self.table.create_record(student_id=1, first_name="John", second_name="Doe", age=-5, sex="M")
    
    def test_create_record_duplicate_id(self):
        self.table.create_record(student_id=1, first_name="John", second_name="Doe", age=20, sex="M")
        
        with self.assertRaises(DuplicateIDError):
            self.table.create_record(student_id=1, first_name="Jane", second_name="Smith", age=22, sex="F")
    
    def test_select_record_no_filters(self):
        self.table.create_record(student_id=1, first_name="John", second_name="Doe", age=20, sex="M")
        self.table.create_record(student_id=2, first_name="Jane", second_name="Smith", age=22, sex="F")
        
        records = self.table.select_record()
        self.assertEqual(len(records), 2)
    
    def test_select_record_by_id(self):
        self.table.create_record(student_id=1, first_name="John", second_name="Doe", age=20, sex="M")
        self.table.create_record(student_id=2, first_name="Jane", second_name="Smith", age=22, sex="F")
        
        records = self.table.select_record(student_id=1)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["first_name"], "John")
    
    def test_select_record_by_first_name(self):
        self.table.create_record(student_id=1, first_name="John", second_name="Doe", age=20, sex="M")
        self.table.create_record(student_id=2, first_name="John", second_name="Smith", age=22, sex="M")
        
        records = self.table.select_record(first_name="John")
        self.assertEqual(len(records), 2)
    
    def test_select_record_by_age(self):
        self.table.create_record(student_id=1, first_name="John", second_name="Doe", age=20, sex="M")
        self.table.create_record(student_id=2, first_name="Jane", second_name="Smith", age=20, sex="F")
        
        records = self.table.select_record(age=20)
        self.assertEqual(len(records), 2)
    
    def test_update_record_success(self):
        self.table.create_record(student_id=1, first_name="John", second_name="Doe", age=20, sex="M")
        
        updated = self.table.update_record(student_id=1, first_name="Jonathan", age=25)
        
        self.assertEqual(updated["first_name"], "Jonathan")
        self.assertEqual(updated["age"], 25)
        self.assertEqual(updated["second_name"], "Doe")
    
    def test_update_record_not_found(self):
        with self.assertRaises(KeyError):
            self.table.update_record(student_id=99, first_name="Jonathan")
    
    def test_update_record_negative_age(self):
        self.table.create_record(student_id=1, first_name="John", second_name="Doe", age=20, sex="M")
        
        with self.assertRaises(InvalidAgeError):
            self.table.update_record(student_id=1, age=-5)
    
    def test_delete_record_success(self):
        self.table.create_record(student_id=1, first_name="John", second_name="Doe", age=20, sex="M")
        
        deleted = self.table.delete_record(1)
        
        self.assertEqual(deleted["student_id"], 1)
        self.assertEqual(len(self.table.get_all()), 0)
    
    def test_delete_record_not_found(self):
        with self.assertRaises(KeyError):
            self.table.delete_record(99)
    
    def test_sort_records_by_id_ascending(self):
        self.table.create_record(student_id=3, first_name="John", second_name="Doe", age=20, sex="M")
        self.table.create_record(student_id=1, first_name="Alice", second_name="Smith", age=22, sex="F")
        self.table.create_record(student_id=2, first_name="Bob", second_name="Brown", age=21, sex="M")
        
        sorted_records = self.table.sort_records("student_id", reverse=False)
        
        self.assertEqual(sorted_records[0]["student_id"], 1)
        self.assertEqual(sorted_records[1]["student_id"], 2)
        self.assertEqual(sorted_records[2]["student_id"], 3)
    
    def test_get_all(self):
        self.table.create_record(student_id=1, first_name="John", second_name="Doe", age=20, sex="M")
        self.table.create_record(student_id=2, first_name="Jane", second_name="Smith", age=22, sex="F")
        
        all_records = self.table.get_all()
        self.assertEqual(len(all_records), 2)


if __name__ == "__main__":
    unittest.main() 