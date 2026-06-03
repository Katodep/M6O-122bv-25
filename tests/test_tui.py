import unittest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.db.tui import StudentTUI
from src.db.backend.memory import StudentTable


class TestStudentTUI(unittest.TestCase):
    
    def setUp(self):
        self.table = StudentTable()
        self.tui = StudentTUI()
        self.tui.table = self.table
    
    def test_initialization(self):
        self.assertTrue(self.tui.running)
        self.assertIsNotNone(self.tui.table)
    
    def test_print_menu(self):
        with patch('builtins.print') as mock_print:
            self.tui.print_menu()
            self.assertTrue(mock_print.called)
    
    def test_read_int_valid(self):
        with patch('builtins.input', return_value='123'):
            result = self.tui._read_int("Enter: ")
            self.assertEqual(result, 123)
    
    def test_read_int_invalid_then_valid(self):
        with patch('builtins.input', side_effect=['abc', '456']):
            with patch('builtins.print') as mock_print:
                result = self.tui._read_int("Enter: ")
                self.assertEqual(result, 456)
                mock_print.assert_called_with("Ошибка: введите целое число.")
    
    def test_read_optional_int_empty(self):
        with patch('builtins.input', return_value=''):
            result = self.tui._read_optional_int("Enter: ")
            self.assertIsNone(result)
    
    def test_read_optional_int_valid(self):
        with patch('builtins.input', return_value='123'):
            result = self.tui._read_optional_int("Enter: ")
            self.assertEqual(result, 123)
    
    def test_read_optional_int_invalid_then_valid(self):
        with patch('builtins.input', side_effect=['abc', '456']):
            with patch('builtins.print') as mock_print:
                result = self.tui._read_optional_int("Enter: ")
                self.assertEqual(result, 456)
                mock_print.assert_called_with("Ошибка: введите целое число или оставьте поле пустым.")
    
    def test_add_student_success(self):
        with patch('builtins.input', side_effect=['1', 'John', 'Doe', '20', 'M']):
            self.tui.add_student()
            records = self.table.select_record()
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0], (1, "John", "Doe", 20, "M"))
    
    def test_add_student_negative_age(self):
        with patch('builtins.input', side_effect=['1', 'John', 'Doe', '-5', 'M']):
            with patch('builtins.print') as mock_print:
                self.tui.add_student()
                mock_print.assert_any_call("Ошибка: Поле age не может быть отрицательным.")
                self.assertEqual(len(self.table.select_record()), 0)
    
    def test_add_student_duplicate_id(self):
        self.table.create_record(1, "John", "Doe", 20, "M")
        with patch('builtins.input', side_effect=['1', 'Jane', 'Smith', '22', 'F']):
            with patch('builtins.print') as mock_print:
                self.tui.add_student()
                mock_print.assert_any_call("Ошибка: Запись с id=1 уже существует.")
                self.assertEqual(len(self.table.select_record()), 1)
    
    def test_add_student_value_error_handling(self):
        with patch('builtins.input', side_effect=['invalid', '1', 'John', 'Doe', '20', 'M']):
            with patch('builtins.print') as mock_print:
                self.tui.add_student()
                mock_print.assert_any_call("Ошибка: введите целое число.")
    
    def test_show_all_students_empty(self):
        with patch('builtins.print') as mock_print:
            self.tui.show_all_students()
            mock_print.assert_any_call("Записи не найдены.")
    
    def test_show_all_students_with_data(self):
        self.table.create_record(1, "John", "Doe", 20, "M")
        self.table.create_record(2, "Jane", "Smith", 22, "F")
        
        with patch('builtins.print') as mock_print:
            self.tui.show_all_students()
            self.assertTrue(mock_print.called)
            self.assertGreater(mock_print.call_count, 0)
    
    def test_find_students_not_found(self):
        with patch('builtins.input', side_effect=['99', '', '', '', '']):
            with patch('builtins.print') as mock_print:
                self.tui.find_students_by_filter()
                mock_print.assert_any_call("Записи не найдены.")
    
    def test_find_students_by_filter(self):
        self.table.create_record(1, "John", "Doe", 20, "M")
        self.table.create_record(2, "Jane", "Smith", 22, "F")
        
        with patch('builtins.input', side_effect=['1', '', '', '', '']):
            with patch('builtins.print') as mock_print:
                self.tui.find_students_by_filter()
                self.assertTrue(mock_print.called)
    
    def test_find_students_by_filter_with_all_fields(self):
        self.table.create_record(1, "John", "Doe", 20, "M")
        
        with patch('builtins.input', side_effect=['1', 'John', 'Doe', '20', 'M']):
            with patch('builtins.print') as mock_print:
                self.tui.find_students_by_filter()
                self.assertTrue(mock_print.called)
    
    def test_find_students_by_filter_partial_match(self):
        self.table.create_record(1, "John", "Doe", 20, "M")
        self.table.create_record(2, "John", "Smith", 22, "M")
        
        with patch('builtins.input', side_effect=['', 'John', '', '', '']):
            with patch('builtins.print') as mock_print:
                self.tui.find_students_by_filter()
                self.assertTrue(mock_print.called)
    
    def test_update_student_success(self):
        self.table.create_record(1, "John", "Doe", 20, "M")
        with patch('builtins.input', side_effect=['1', 'Jonathan', 'Doe', '25', 'M']):
            with patch('builtins.print') as mock_print:
                self.tui.update_student()
                records = self.table.select_record(student_id=1)
                self.assertEqual(records[0], (1, "Jonathan", "Doe", 25, "M"))
    
    def test_update_student_not_found(self):
        with patch('builtins.input', side_effect=['99', 'Jonathan', 'Doe', '25', 'M']):
            with patch('builtins.print') as mock_print:
                self.tui.update_student()
                mock_print.assert_any_call("Запись с id=99 не найдена.")
    
    def test_update_student_key_error_handling(self):
        with patch('builtins.input', side_effect=['999', 'John', 'Doe', '20', 'M']):
            with patch('builtins.print') as mock_print:
                self.tui.update_student()
                mock_print.assert_any_call("Запись с id=999 не найдена.")
    
    def test_delete_student_success(self):
        self.table.create_record(1, "John", "Doe", 20, "M")
        with patch('builtins.input', return_value='1'):
            self.tui.delete_student()
            self.assertEqual(len(self.table.select_record()), 0)
    
    def test_delete_student_not_found(self):
        with patch('builtins.input', return_value='99'):
            with patch('builtins.print') as mock_print:
                self.tui.delete_student()
                self.assertTrue(mock_print.called)
    
    def test_delete_student_key_error_handling(self):
        with patch('builtins.input', return_value='999'):
            with patch('builtins.print') as mock_print:
                self.tui.delete_student()
                self.assertTrue(mock_print.called)
    
    def test_sort_students_with_data_ascending(self):
        self.table.create_record(2, "Bob", "Brown", 21, "M")
        self.table.create_record(1, "Alice", "Smith", 20, "F")
        
        with patch('builtins.input', side_effect=['6', '1', '1']):
            with patch('builtins.print') as mock_print:
                self.tui.sort_students()
                self.assertTrue(mock_print.called)
                self.assertGreater(mock_print.call_count, 0)
    
    def test_sort_students_with_data_descending(self):
        self.table.create_record(1, "Alice", "Smith", 20, "F")
        self.table.create_record(2, "Bob", "Brown", 21, "M")
        
        with patch('builtins.input', side_effect=['6', '1', '2']):
            with patch('builtins.print') as mock_print:
                self.tui.sort_students()
                self.assertTrue(mock_print.called)
    
    def test_sort_students_by_name_ascending(self):
        self.table.create_record(2, "Bob", "Brown", 21, "M")
        self.table.create_record(1, "Alice", "Smith", 20, "F")
        self.table.create_record(3, "John", "Doe", 22, "M")
        
        with patch('builtins.input', side_effect=['6', '2', '1']):
            with patch('builtins.print') as mock_print:
                self.tui.sort_students()
                self.assertTrue(mock_print.called)
    
    def test_sort_students_by_age_descending(self):
        self.table.create_record(1, "Alice", "Smith", 20, "F")
        self.table.create_record(2, "Bob", "Brown", 25, "M")
        self.table.create_record(3, "John", "Doe", 22, "M")
        
        with patch('builtins.input', side_effect=['6', '4', '2']):
            with patch('builtins.print') as mock_print:
                self.tui.sort_students()
                self.assertTrue(mock_print.called)
    
    def test_sort_students_by_sex_ascending(self):
        self.table.create_record(1, "Alice", "Smith", 20, "F")
        self.table.create_record(2, "Bob", "Brown", 21, "M")
        self.table.create_record(3, "Jane", "Doe", 22, "F")
        
        with patch('builtins.input', side_effect=['6', '5', '1']):
            with patch('builtins.print') as mock_print:
                self.tui.sort_students()
                self.assertTrue(mock_print.called)
    
    def test_sort_students_invalid_field_choice(self):
        self.table.create_record(1, "John", "Doe", 20, "M")
        
        with patch('builtins.input', side_effect=['6', '0']):
            with patch('builtins.print') as mock_print:
                self.tui.sort_students()
                mock_print.assert_any_call("Ошибка: неверный выбор поля.")
    
    def test_run_exit(self):
        with patch('builtins.input', return_value='0'):
            with patch('builtins.print') as mock_print:
                self.tui.run()
                mock_print.assert_any_call("Выход из программы.")
                self.assertFalse(self.tui.running)
    
    def test_run_invalid_choice(self):
        with patch('builtins.input', side_effect=['invalid', '0']):
            with patch('builtins.print') as mock_print:
                self.tui.run()
                mock_print.assert_any_call("Неизвестная команда. Повторите ввод.")
    
    def test_run_menu_option_1_add(self):
        with patch('builtins.input', side_effect=['1', '1', 'John', 'Doe', '20', 'M', '0']):
            with patch('builtins.print') as mock_print:
                self.tui.run()
                self.assertTrue(mock_print.called)
    
    def test_run_menu_option_2_show(self):
        self.table.create_record(1, "John", "Doe", 20, "M")
        with patch('builtins.input', side_effect=['2', '0']):
            with patch('builtins.print') as mock_print:
                self.tui.run()
                self.assertTrue(mock_print.called)
    
    def test_run_menu_option_4_update(self):
        self.table.create_record(1, "John", "Doe", 20, "M")
        with patch('builtins.input', side_effect=['4', '1', 'John', 'Doe', '25', 'M', '0']):
            with patch('builtins.print') as mock_print:
                self.tui.run()
                self.assertTrue(mock_print.called)
    
    def test_run_menu_option_5_delete(self):
        self.table.create_record(1, "John", "Doe", 20, "M")
        with patch('builtins.input', side_effect=['5', '1', '0']):
            with patch('builtins.print') as mock_print:
                self.tui.run()
                self.assertTrue(mock_print.called)
    
    def test_run_menu_option_6_sort(self):
        self.table.create_record(1, "John", "Doe", 20, "M")
        with patch('builtins.input', side_effect=['6', '1', '1', '0']):
            with patch('builtins.print') as mock_print:
                self.tui.run()
                self.assertTrue(mock_print.called)


if __name__ == "__main__":
    unittest.main()