import unittest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.db.backend.memory import MemoryDatabase


class TestStudentTUI(unittest.TestCase):
    
    def setUp(self):
        with patch('builtins.input', return_value='1'):
            from src.db.tui import StudentTUI
            self.tui = StudentTUI()
            self.tui.database = MemoryDatabase()
            self.tui._ensure_table_exists = self._mock_ensure_table
    
    def _mock_ensure_table(self):
        try:
            self.tui.database.select_records("students")
        except:
            self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
    
    def test_initialization(self):
        self.assertTrue(self.tui.running)
        self.assertIsNotNone(self.tui.database)
    
    def test_print_menu(self):
        with patch('builtins.print') as mock_print:
            self.tui.print_menu()
            self.assertTrue(mock_print.called)
    
    def test_add_student_success(self):
        self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
        with patch('builtins.input', side_effect=['1', 'John', 'Doe', '20', 'M']):
            with patch('builtins.print'):
                self.tui.add_student()
                records = self.tui.database.select_records("students")
                self.assertEqual(len(records), 1)
                self.assertEqual(records[0]["student_id"], 1)
    
    def test_add_student_negative_age(self):
        self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
        with patch('builtins.input', side_effect=['1', 'John', 'Doe', '-5', 'M']):
            with patch('builtins.print') as mock_print:
                self.tui.add_student()
                mock_print.assert_any_call("Ошибка: возраст не может быть отрицательным.")
    
    def test_add_student_duplicate_id(self):
        self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
        self.tui.database.insert_record("students", {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"})
        with patch('builtins.input', side_effect=['1', 'Jane', 'Smith', '22', 'F']):
            with patch('builtins.print') as mock_print:
                self.tui.add_student()
                self.assertTrue(mock_print.called)
    
    def test_show_all_students_empty(self):
        self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
        with patch('builtins.print') as mock_print:
            self.tui.show_all_students()
            mock_print.assert_any_call("Записи не найдены.")
    
    def test_show_all_students_with_data(self):
        self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
        self.tui.database.insert_record("students", {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"})
        with patch('builtins.print') as mock_print:
            self.tui.show_all_students()
            self.assertTrue(mock_print.called)
    
    def test_find_students_not_found(self):
        self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
        with patch('builtins.input', side_effect=['99', '', '', '', '']):
            with patch('builtins.print') as mock_print:
                self.tui.find_students()
                mock_print.assert_any_call("Записи не найдены.")
    
    def test_find_students_by_filter(self):
        self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
        self.tui.database.insert_record("students", {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"})
        with patch('builtins.input', side_effect=['1', '', '', '', '']):
            with patch('builtins.print') as mock_print:
                self.tui.find_students()
                self.assertTrue(mock_print.called)
    
    def test_update_student_success(self):
        self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
        self.tui.database.insert_record("students", {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"})
        with patch('builtins.input', side_effect=['1', 'Jonathan', 'Doe', '25', 'M']):
            with patch('builtins.print'):
                self.tui.update_student()
                records = self.tui.database.select_records("students", student_id=1)
                self.assertEqual(records[0]["first_name"], "Jonathan")
                self.assertEqual(records[0]["age"], 25)
    
    def test_update_student_not_found(self):
        self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
        with patch('builtins.input', side_effect=['99', 'Jonathan', 'Doe', '25', 'M']):
            with patch('builtins.print') as mock_print:
                self.tui.update_student()
                mock_print.assert_any_call("Студент с ID 99 не найден.")
    
    def test_delete_student_success(self):
        self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
        self.tui.database.insert_record("students", {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"})
        with patch('builtins.input', return_value='1'):
            with patch('builtins.print'):
                self.tui.delete_student()
                records = self.tui.database.select_records("students")
                self.assertEqual(len(records), 0)
    
    def test_delete_student_not_found(self):
        self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
        with patch('builtins.input', return_value='99'):
            with patch('builtins.print') as mock_print:
                self.tui.delete_student()
                mock_print.assert_any_call("Студент с ID 99 не найден.")
    
    def test_run_exit(self):
        with patch('builtins.input', return_value='0'):
            with patch('builtins.print'):
                self.tui.run()
                self.assertFalse(self.tui.running)
    
    def test_run_invalid_choice(self):
        with patch('builtins.input', side_effect=['invalid', '0']):
            with patch('builtins.print') as mock_print:
                self.tui.run()
                mock_print.assert_any_call("Неверный выбор. Попробуйте снова.")
    
    def test_show_info(self):
        with patch('builtins.print') as mock_print:
            self.tui.show_info()
            self.assertTrue(mock_print.called)
    
    def test_sort_students_by_id_ascending(self):
        self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
        self.tui.database.insert_record("students", {"student_id": 3, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"})
        self.tui.database.insert_record("students", {"student_id": 1, "first_name": "Alice", "second_name": "Smith", "age": 22, "sex": "F"})
        
        with patch('builtins.input', side_effect=['1', '1']):
            with patch('builtins.print') as mock_print:
                self.tui.sort_students()
                self.assertTrue(mock_print.called)
    
    def test_sort_students_empty(self):
        self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
        
        with patch('builtins.input', side_effect=['1', '1']):
            with patch('builtins.print') as mock_print:
                self.tui.sort_students()
                self.assertTrue(mock_print.called)
    
    def test_sort_students_invalid_field(self):
        self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
        self.tui.database.insert_record("students", {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"})
        
        with patch('builtins.input', side_effect=['0', '1']):
            with patch('builtins.print') as mock_print:
                self.tui.sort_students()
                self.assertTrue(mock_print.called)
    
    def test_find_students_with_all_filters(self):
        self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
        self.tui.database.insert_record("students", {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"})
        
        with patch('builtins.input', side_effect=['1', 'John', 'Doe', '20', 'M']):
            with patch('builtins.print') as mock_print:
                self.tui.find_students()
                self.assertTrue(mock_print.called)
    
    def test_sort_students_with_data_descending(self):
        self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
        self.tui.database.insert_record("students", {"student_id": 1, "first_name": "Alice", "second_name": "Smith", "age": 20, "sex": "F"})
        self.tui.database.insert_record("students", {"student_id": 2, "first_name": "Bob", "second_name": "Brown", "age": 25, "sex": "M"})
        
        with patch('builtins.input', side_effect=['1', '2']):
            with patch('builtins.print') as mock_print:
                self.tui.sort_students()
                self.assertTrue(mock_print.called)
    
    def test_sort_students_invalid_order(self):
        self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
        self.tui.database.insert_record("students", {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"})
        
        with patch('builtins.input', side_effect=['1', '3']):
            with patch('builtins.print') as mock_print:
                self.tui.sort_students()
                self.assertTrue(mock_print.called)
    
    def test_select_database_type_memory(self):
        with patch('builtins.input', return_value='1'):
            with patch('builtins.print') as mock_print:
                from src.db.tui import StudentTUI
                tui = StudentTUI()
                mock_print.assert_any_call("Используется in-memory база данных")
    
    def test_select_database_type_json(self):
        with patch('builtins.input', return_value='2'):
            with patch('builtins.print') as mock_print:
                from src.db.tui import StudentTUI
                tui = StudentTUI()
                mock_print.assert_any_call("Используется файловая база данных (JSON, папка 'data/')")
    
    def test_select_database_type_csv(self):
        with patch('builtins.input', return_value='3'):
            with patch('builtins.print') as mock_print:
                from src.db.tui import StudentTUI
                tui = StudentTUI()
                mock_print.assert_any_call("Используется файловая база данных (CSV, папка 'data_csv/')")
    
    def test_ensure_table_exists_creates_table(self):
        self.tui.database = MemoryDatabase()
        self.tui._ensure_table_exists()
        records = self.tui.database.select_records("students")
        self.assertEqual(len(records), 0)
    
    def test_read_int_valid(self):
        with patch('builtins.input', return_value='42'):
            result = self.tui._read_int("Enter: ")
            self.assertEqual(result, 42)
    
    def test_read_int_invalid_then_valid(self):
        with patch('builtins.input', side_effect=['abc', '42']):
            with patch('builtins.print') as mock_print:
                result = self.tui._read_int("Enter: ")
                self.assertEqual(result, 42)
                mock_print.assert_any_call("Ошибка: введите целое число.")
    
    def test_read_optional_int_empty(self):
        with patch('builtins.input', return_value=''):
            result = self.tui._read_optional_int("Enter: ")
            self.assertIsNone(result)
    
    def test_read_optional_int_valid(self):
        with patch('builtins.input', return_value='42'):
            result = self.tui._read_optional_int("Enter: ")
            self.assertEqual(result, 42)
    
    def test_read_optional_int_invalid_then_valid(self):
        with patch('builtins.input', side_effect=['abc', '42']):
            with patch('builtins.print') as mock_print:
                result = self.tui._read_optional_int("Enter: ")
                self.assertEqual(result, 42)
                mock_print.assert_any_call("Ошибка: введите целое число или оставьте поле пустым.")
    
    def test_print_records_empty(self):
        with patch('builtins.print') as mock_print:
            self.tui._print_records([])
            mock_print.assert_any_call("Записи не найдены.")
    
    def test_print_records_with_data(self):
        records = [{"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"}]
        with patch('builtins.print') as mock_print:
            self.tui._print_records(records)
            self.assertTrue(mock_print.called)
    
    def test_sort_students_by_age_ascending(self):
        self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
        self.tui.database.insert_record("students", {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 25, "sex": "M"})
        self.tui.database.insert_record("students", {"student_id": 2, "first_name": "Alice", "second_name": "Smith", "age": 20, "sex": "F"})
        
        with patch('builtins.input', side_effect=['4', '1']):
            with patch('builtins.print') as mock_print:
                self.tui.sort_students()
                self.assertTrue(mock_print.called)
    
    def test_sort_students_by_sex_ascending(self):
        self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
        self.tui.database.insert_record("students", {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"})
        self.tui.database.insert_record("students", {"student_id": 2, "first_name": "Alice", "second_name": "Smith", "age": 22, "sex": "F"})
        
        with patch('builtins.input', side_effect=['5', '1']):
            with patch('builtins.print') as mock_print:
                self.tui.sort_students()
                self.assertTrue(mock_print.called)
    
    def test_find_students_with_partial_match(self):
        self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
        self.tui.database.insert_record("students", {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"})
        self.tui.database.insert_record("students", {"student_id": 2, "first_name": "John", "second_name": "Smith", "age": 22, "sex": "M"})
        
        with patch('builtins.input', side_effect=['', 'John', '', '', '']):
            with patch('builtins.print') as mock_print:
                self.tui.find_students()
                self.assertTrue(mock_print.called)
    
    def test_update_student_with_age_conversion_error(self):
        self.tui.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
        self.tui.database.insert_record("students", {"student_id": 1, "first_name": "John", "second_name": "Doe", "age": 20, "sex": "M"})
        
        with patch('builtins.input', side_effect=['1', '', '', 'invalid', '']):
            with patch('builtins.print') as mock_print:
                self.tui.update_student()
                mock_print.assert_any_call("Ошибка: введите целое число.")


if __name__ == "__main__":
    unittest.main()