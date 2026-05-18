import unittest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.db.tui import (
    _table,
    _print_menu,
    _read_int,
    _add_student,
    _print_records,
    _show_all_students,
    _read_optional_int,
    _find_students_by_filter,
    _delete_student,
    run
)


class TestTUI(unittest.TestCase):
    
    def setUp(self):
        while len(_table.select_record()) > 0:
            _table.delete_record(_table.select_record()[0][0])
    
    def test_table_exists(self):
        self.assertIsNotNone(_table)
        self.assertEqual(len(_table.select_record()), 0)
    
    def test_print_menu(self):
        with patch('builtins.print') as mock_print:
            _print_menu()
            self.assertTrue(mock_print.called)
    
    def test_read_int_valid(self):
        with patch('builtins.input', return_value='123'):
            result = _read_int("Enter: ")
            self.assertEqual(result, 123)
    
    def test_read_int_invalid_then_valid(self):
        with patch('builtins.input', side_effect=['abc', '456']):
            with patch('builtins.print') as mock_print:
                result = _read_int("Enter: ")
                self.assertEqual(result, 456)
                mock_print.assert_called_with("Ошибка: введите целое число.")
    
    def test_add_student_success(self):
        with patch('builtins.input', side_effect=['1', 'John', 'Doe', '20', 'M']):
            _add_student()            
            records = _table.select_record()
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0], (1, "John", "Doe", 20, "M"))
    
    def test_add_student_negative_age(self):
        with patch('builtins.input', side_effect=['1', 'John', 'Doe', '-5', 'M']):
            with patch('builtins.print') as mock_print:
                _add_student()
                mock_print.assert_any_call("Ошибка: Поле age не может быть отрицательным.")
                self.assertEqual(len(_table.select_record()), 0)
    
    def test_add_student_duplicate_id(self):
        _table.create_record(1, "John", "Doe", 20, "M")
        
        with patch('builtins.input', side_effect=['1', 'Jane', 'Smith', '22', 'F']):
            with patch('builtins.print') as mock_print:
                _add_student()
                mock_print.assert_any_call("Ошибка: Запись с id=1 уже существует.")
                self.assertEqual(len(_table.select_record()), 1)
    
    def test_print_records_empty(self):
        with patch('builtins.print') as mock_print:
            _print_records([])
            mock_print.assert_called_with("Записи не найдены.")
    
    def test_print_records_with_data(self):
        records = [(1, "John", "Doe", 20, "M"), (2, "Jane", "Smith", 22, "F")]
        with patch('builtins.print') as mock_print:
            _print_records(records)
            self.assertTrue(mock_print.called)
            self.assertTrue(any("John" in str(call) for call in mock_print.call_args_list))
    
    def test_show_all_students_empty(self):
        with patch('builtins.print') as mock_print:
            _show_all_students()
            mock_print.assert_any_call("Записи не найдены.")
    
    def test_show_all_students_with_data(self):
        _table.create_record(1, "John", "Doe", 20, "M")
        _table.create_record(2, "Jane", "Smith", 22, "F")
        
        with patch('builtins.print') as mock_print:
            _show_all_students()
            self.assertTrue(mock_print.called)
            self.assertTrue(any("John" in str(call) for call in mock_print.call_args_list))
    
    def test_read_optional_int_empty(self):
        with patch('builtins.input', return_value=''):
            result = _read_optional_int("Enter: ")
            self.assertIsNone(result)
    
    def test_read_optional_int_valid(self):
        with patch('builtins.input', return_value='123'):
            result = _read_optional_int("Enter: ")
            self.assertEqual(result, 123)
    
    def test_read_optional_int_invalid_then_valid(self):
        with patch('builtins.input', side_effect=['abc', '456']):
            with patch('builtins.print') as mock_print:
                result = _read_optional_int("Enter: ")
                self.assertEqual(result, 456)
                mock_print.assert_called_with("Ошибка: введите целое число или оставьте поле пустым.")
    
    def test_find_by_id(self):
        _table.create_record(1, "John", "Doe", 20, "M")
        _table.create_record(2, "Jane", "Smith", 22, "F")
        
        with patch('builtins.input', side_effect=['1', '', '', '', '']):
            with patch('builtins.print') as mock_print:
                _find_students_by_filter()
                
                self.assertTrue(mock_print.called)
    
    def test_find_by_first_name(self):
        _table.create_record(1, "John", "Doe", 20, "M")
        _table.create_record(2, "John", "Smith", 22, "M")
        
        with patch('builtins.input', side_effect=['', 'John', '', '', '']):
            with patch('builtins.print') as mock_print:
                _find_students_by_filter()
                self.assertTrue(mock_print.called)
    
    def test_find_not_found(self):
        _table.create_record(1, "John", "Doe", 20, "M")
        
        with patch('builtins.input', side_effect=['99', '', '', '', '']):
            with patch('builtins.print') as mock_print:
                _find_students_by_filter()
                mock_print.assert_any_call("Записи не найдены.")
    
    def test_delete_student_success(self):
        _table.create_record(1, "John", "Doe", 20, "M")
        _table.create_record(2, "Jane", "Smith", 22, "F")
        
        with patch('builtins.input', return_value='1'):
            with patch('builtins.print') as mock_print:
                _delete_student()
                self.assertTrue(mock_print.called)
                self.assertEqual(len(_table.select_record()), 1)
    
    def test_delete_student_not_found(self):
        _table.create_record(1, "John", "Doe", 20, "M")
        
        with patch('builtins.input', return_value='99'):
            with patch('builtins.print') as mock_print:
                _delete_student()
                self.assertTrue(mock_print.called)
                self.assertTrue(any("99" in str(call) for call in mock_print.call_args_list))
                self.assertEqual(len(_table.select_record()), 1)
    
    def test_run_exit(self):
        with patch('builtins.input', return_value='0'):
            with patch('builtins.print') as mock_print:
                run()
                mock_print.assert_any_call("Выход из программы.")


if __name__ == "__main__":
    unittest.main()