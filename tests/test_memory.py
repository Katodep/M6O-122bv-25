import unittest
import sys
import os

# Добавляем путь к src
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.db.backend.memory import StudentTable
from src.db.backend.errors import InvalidAgeError, DuplicateIDError


class TestStudentTable(unittest.TestCase):
    
    def setUp(self):
        """Создание новой таблицы перед каждым тестом"""
        self.table = StudentTable()
    
    # ============= ТЕСТЫ CREATE_RECORD =============
    
    def test_create_record_success(self):
        """Успешное создание записи"""
        record = self.table.create_record(1, "John", "Doe", 20, "M")
        self.assertEqual(record, (1, "John", "Doe", 20, "M"))
        self.assertEqual(len(self.table.select_record()), 1)
    
    def test_create_record_multiple(self):
        """Создание нескольких записей"""
        records = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Bob", "Brown", 21, "M"),
        ]
        for record in records:
            self.table.create_record(*record)
        
        all_records = self.table.select_record()
        self.assertEqual(len(all_records), 3)
        self.assertEqual(all_records, records)
    
    def test_create_record_strip_whitespace(self):
        """Удаление пробелов при создании"""
        record = self.table.create_record(1, "  John  ", "  Doe  ", 20, "  M  ")
        self.assertEqual(record, (1, "John", "Doe", 20, "M"))
    
    def test_create_record_negative_age(self):
        """Ошибка при отрицательном возрасте"""
        with self.assertRaises(InvalidAgeError) as context:
            self.table.create_record(1, "John", "Doe", -5, "M")
        self.assertEqual(str(context.exception), "Поле age не может быть отрицательным.")
    
    def test_create_record_zero_age(self):
        """Нулевой возраст допустим"""
        record = self.table.create_record(1, "John", "Doe", 0, "M")
        self.assertEqual(record, (1, "John", "Doe", 0, "M"))
    
    def test_create_record_duplicate_id(self):
        """Ошибка при дубликате ID"""
        self.table.create_record(1, "John", "Doe", 20, "M")
        with self.assertRaises(DuplicateIDError) as context:
            self.table.create_record(1, "Jane", "Smith", 22, "F")
        self.assertEqual(str(context.exception), "Запись с id=1 уже существует.")
    
    def test_create_record_empty_strings(self):
        """Пустые строки допустимы"""
        record = self.table.create_record(1, "", "", 20, "")
        self.assertEqual(record, (1, "", "", 20, ""))
    
    # ============= ТЕСТЫ SELECT_RECORD =============
    
    def test_select_empty_table(self):
        """Выборка из пустой таблицы"""
        self.assertEqual(self.table.select_record(), [])
        self.assertEqual(self.table.select_record(student_id=1), [])
    
    def test_select_no_filters(self):
        """Выборка без фильтров"""
        records = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
        ]
        for record in records:
            self.table.create_record(*record)
        
        result = self.table.select_record()
        self.assertEqual(result, records)
    
    def test_select_by_id(self):
        """Фильтр по ID"""
        records = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Bob", "Brown", 21, "M"),
        ]
        for record in records:
            self.table.create_record(*record)
        
        result = self.table.select_record(student_id=2)
        self.assertEqual(result, [records[1]])
        
        result = self.table.select_record(student_id=99)
        self.assertEqual(result, [])
    
    def test_select_by_first_name(self):
        """Фильтр по имени"""
        records = [
            (1, "John", "Doe", 20, "M"),
            (2, "John", "Smith", 22, "M"),
            (3, "Jane", "Doe", 21, "F"),
        ]
        for record in records:
            self.table.create_record(*record)
        
        result = self.table.select_record(first_name="John")
        self.assertEqual(result, [records[0], records[1]])
    
    def test_select_by_second_name(self):
        """Фильтр по фамилии"""
        records = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Doe", 22, "F"),
            (3, "Bob", "Smith", 21, "M"),
        ]
        for record in records:
            self.table.create_record(*record)
        
        result = self.table.select_record(second_name="Doe")
        self.assertEqual(result, [records[0], records[1]])
    
    def test_select_by_age(self):
        """Фильтр по возрасту"""
        records = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 20, "F"),
            (3, "Bob", "Brown", 21, "M"),
        ]
        for record in records:
            self.table.create_record(*record)
        
        result = self.table.select_record(age=20)
        self.assertEqual(result, [records[0], records[1]])
    
    def test_select_by_sex(self):
        """Фильтр по полу"""
        records = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Bob", "Brown", 21, "M"),
            (4, "Alice", "Jones", 19, "F"),
        ]
        for record in records:
            self.table.create_record(*record)
        
        males = self.table.select_record(sex="M")
        self.assertEqual(males, [records[0], records[2]])
        
        females = self.table.select_record(sex="F")
        self.assertEqual(females, [records[1], records[3]])
    
    def test_select_multiple_filters(self):
        """Комбинация фильтров"""
        self.table.create_record(1, "John", "Doe", 20, "M")
        self.table.create_record(2, "John", "Doe", 25, "M")
        self.table.create_record(3, "John", "Smith", 20, "M")
        self.table.create_record(4, "Jane", "Doe", 20, "F")
        
        result = self.table.select_record(first_name="John", second_name="Doe", age=20)
        self.assertEqual(result, [(1, "John", "Doe", 20, "M")])
    
    def test_select_returns_copy(self):
        """Проверка, что возвращается копия списка"""
        self.table.create_record(1, "John", "Doe", 20, "M")
        
        result = self.table.select_record()
        result.append((99, "Extra", "Person", 99, "X"))
        
        # Оригинал не должен измениться
        self.assertEqual(len(self.table.select_record()), 1)
    
    # ============= ТЕСТЫ UPDATE_RECORD =============
    
    def test_update_record_success(self):
        """Успешное обновление записи"""
        self.table.create_record(1, "John", "Doe", 20, "M")
        
        updated = self.table.update_record(1, "Jonathan", "Doe", 21, "M")
        self.assertEqual(updated, (1, "Jonathan", "Doe", 21, "M"))
        
        # Проверяем в таблице
        record = self.table.select_record(student_id=1)
        self.assertEqual(record[0], (1, "Jonathan", "Doe", 21, "M"))
    
    def test_update_record_all_fields(self):
        """Обновление всех полей"""
        self.table.create_record(1, "John", "Doe", 20, "M")
        
        updated = self.table.update_record(1, "Jane", "Smith", 25, "F")
        self.assertEqual(updated, (1, "Jane", "Smith", 25, "F"))
    
    def test_update_record_strip_whitespace(self):
        """Удаление пробелов при обновлении"""
        self.table.create_record(1, "John", "Doe", 20, "M")
        
        updated = self.table.update_record(1, "  Jonathan  ", "  Doe  ", 21, "  M  ")
        self.assertEqual(updated, (1, "Jonathan", "Doe", 21, "M"))
    
    def test_update_record_not_found(self):
        """Ошибка при обновлении несуществующей записи"""
        self.table.create_record(1, "John", "Doe", 20, "M")
        
        with self.assertRaises(KeyError) as context:
            self.table.update_record(99, "None", "Exists", 20, "M")
        self.assertIn("99", str(context.exception))
    
    def test_update_record_negative_age(self):
        """Ошибка при отрицательном возрасте при обновлении"""
        self.table.create_record(1, "John", "Doe", 20, "M")
        
        with self.assertRaises(InvalidAgeError):
            self.table.update_record(1, "John", "Doe", -5, "M")
        
        # Запись не должна измениться
        record = self.table.select_record(student_id=1)
        self.assertEqual(record[0], (1, "John", "Doe", 20, "M"))
    
    def test_update_record_multiple_times(self):
        """Многократное обновление одной записи"""
        self.table.create_record(1, "John", "Doe", 20, "M")
        
        self.table.update_record(1, "Jonathan", "Doe", 20, "M")
        self.table.update_record(1, "Jonathan", "Johnson", 20, "M")
        updated = self.table.update_record(1, "Jonathan", "Johnson", 25, "M")
        
        self.assertEqual(updated, (1, "Jonathan", "Johnson", 25, "M"))
    
    def test_update_record_preserves_others(self):
        """Обновление не должно влиять на другие записи"""
        self.table.create_record(1, "John", "Doe", 20, "M")
        self.table.create_record(2, "Jane", "Smith", 22, "F")
        
        self.table.update_record(1, "Jonathan", "Doe", 21, "M")
        
        all_records = self.table.select_record()
        expected = [
            (1, "Jonathan", "Doe", 21, "M"),
            (2, "Jane", "Smith", 22, "F"),
        ]
        self.assertEqual(all_records, expected)
    
    # ============= ТЕСТЫ DELETE_RECORD =============
    
    def test_delete_record_success(self):
        """Успешное удаление записи"""
        self.table.create_record(1, "John", "Doe", 20, "M")
        self.table.create_record(2, "Jane", "Smith", 22, "F")
        
        deleted = self.table.delete_record(1)
        self.assertEqual(deleted, (1, "John", "Doe", 20, "M"))
        
        remaining = self.table.select_record()
        self.assertEqual(remaining, [(2, "Jane", "Smith", 22, "F")])
    
    def test_delete_record_middle(self):
        """Удаление записи из середины"""
        records = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Bob", "Brown", 21, "M"),
        ]
        for record in records:
            self.table.create_record(*record)
        
        self.table.delete_record(2)
        
        remaining = self.table.select_record()
        expected = [records[0], records[2]]
        self.assertEqual(remaining, expected)
    
    def test_delete_record_first(self):
        """Удаление первой записи"""
        records = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Bob", "Brown", 21, "M"),
        ]
        for record in records:
            self.table.create_record(*record)
        
        self.table.delete_record(1)
        
        remaining = self.table.select_record()
        expected = [records[1], records[2]]
        self.assertEqual(remaining, expected)
    
    def test_delete_record_last(self):
        """Удаление последней записи"""
        records = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Bob", "Brown", 21, "M"),
        ]
        for record in records:
            self.table.create_record(*record)
        
        self.table.delete_record(3)
        
        remaining = self.table.select_record()
        expected = [records[0], records[1]]
        self.assertEqual(remaining, expected)
    
    def test_delete_record_not_found(self):
        """Ошибка при удалении несуществующей записи"""
        self.table.create_record(1, "John", "Doe", 20, "M")
        
        with self.assertRaises(KeyError) as context:
            self.table.delete_record(99)
        self.assertIn("99", str(context.exception))
    
    def test_delete_record_empty_table(self):
        """Ошибка при удалении из пустой таблицы"""
        with self.assertRaises(KeyError):
            self.table.delete_record(1)
    
    def test_delete_record_consecutive(self):
        """Последовательное удаление нескольких записей"""
        for i in range(1, 6):
            self.table.create_record(i, f"Name{i}", f"Last{i}", 20, "M")
        
        self.table.delete_record(2)
        self.table.delete_record(4)
        self.table.delete_record(1)
        
        remaining = self.table.select_record()
        expected = [
            (3, "Name3", "Last3", 20, "M"),
            (5, "Name5", "Last5", 20, "M"),
        ]
        self.assertEqual(remaining, expected)
    
    # ============= ИНТЕГРАЦИОННЫЕ ТЕСТЫ =============
    
    def test_full_crud_workflow(self):
        """Полный цикл CRUD операций"""
        # CREATE
        self.table.create_record(1, "John", "Doe", 20, "M")
        self.assertEqual(len(self.table.select_record()), 1)
        
        # READ
        record = self.table.select_record(student_id=1)
        self.assertEqual(record[0], (1, "John", "Doe", 20, "M"))
        
        # UPDATE
        self.table.update_record(1, "Jonathan", "Doe", 21, "M")
        
        # READ after UPDATE
        record = self.table.select_record(student_id=1)
        self.assertEqual(record[0], (1, "Jonathan", "Doe", 21, "M"))
        
        # DELETE
        self.table.delete_record(1)
        
        # READ after DELETE
        self.assertEqual(self.table.select_record(), [])
    
    def test_data_integrity(self):
        """Проверка целостности данных при операциях"""
        # Создаем записи
        for i in range(1, 4):
            self.table.create_record(i, f"Name{i}", f"Last{i}", 20 + i, "M")
        
        # Сохраняем копию
        original = self.table.select_record()
        
        # Обновляем одну
        self.table.update_record(2, "Updated", "Name", 30, "F")
        
        # Удаляем другую
        self.table.delete_record(1)
        
        # Проверяем оставшиеся
        remaining = self.table.select_record()
        self.assertEqual(len(remaining), 2)
        self.assertEqual(remaining[0], (2, "Updated", "Name", 30, "F"))
        self.assertEqual(remaining[1], (3, "Name3", "Last3", 23, "M"))


if __name__ == "__main__":
    unittest.main()