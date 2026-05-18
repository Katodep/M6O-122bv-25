import unittest
from src.db.backend.memory import StudentTable
from src.db.backend.errors import InvalidAgeError, DuplicateIDError


class TestMemory(unittest.TestCase):
    def setUp(self):
        """Создание нового экземпляра StudentTable перед каждым тестом"""
        self.student_table = StudentTable()
        self.assertIsInstance(self.student_table, StudentTable)

    # ============= ТЕСТЫ ДЛЯ create_record =============
    
    def test_create_record_success(self):
        """Тест успешного создания записей"""
        cases = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
            (4, "Bob", "Brown", 21, "M"),
            (5, "Charlie", "Davis", 18, "M"),
            (6, "Eve", "Miller", 23, "F"),
            (7, "Frank", "Wilson", 20, "M"),
            (8, "Grace", "Moore", 22, "F"),
            (9, "Hank", "Taylor", 19, "M"),
            (10, "Ivy", "Anderson", 21, "F"),
            (11, "Jack", "Thomas", 18, "M"),
            (12, "Kathy", "Jackson", 23, "F"),
        ]

        for test_data in cases:
            with self.subTest(test_data=test_data):
                record = self.student_table.create_record(*test_data)
                self.assertEqual(record, test_data)
                
        # Проверяем количество записей
        all_records = self.student_table.select_record()
        self.assertEqual(len(all_records), 12)

    def test_create_record_strip_whitespace(self):
        """Тест удаления пробелов при создании"""
        test_data = (1, "  John  ", "  Doe  ", 20, "  M  ")
        expected = (1, "John", "Doe", 20, "M")
        
        record = self.student_table.create_record(*test_data)
        self.assertEqual(record, expected)
        
        # Проверяем сохранение в таблице
        selected = self.student_table.select_record(student_id=1)
        self.assertEqual(selected[0], expected)

    def test_create_record_negative_age(self):
        """Тест создания с отрицательным возрастом"""
        cases = [
            (1, "John", "Doe", -1, "M"),
            (2, "Jane", "Smith", -5, "F"),
            (3, "Alice", "Johnson", -10, "F"),
            (4, "Bob", "Brown", -100, "M"),
        ]
        error_message = "Поле age не может быть отрицательным."

        for test_data in cases:
            with self.subTest(test_data=test_data):
                with self.assertRaises(InvalidAgeError) as context:
                    self.student_table.create_record(*test_data)
                self.assertEqual(str(context.exception), error_message)
                
        # Проверяем, что ничего не добавилось
        self.assertEqual(len(self.student_table.select_record()), 0)

    def test_create_record_zero_age(self):
        """Тест создания с нулевым возрастом (допустимо)"""
        record = self.student_table.create_record(1, "John", "Doe", 0, "M")
        self.assertEqual(record, (1, "John", "Doe", 0, "M"))

    def test_create_record_duplicate_id(self):
        """Тест создания дубликата ID"""
        test_data_1 = (1, "John", "Doe", 20, "M")
        test_data_2 = (1, "Jane", "Smith", 22, "F")
        error_message = "Запись с id=1 уже существует."

        self.student_table.create_record(*test_data_1)

        with self.assertRaises(DuplicateIDError) as context:
            self.student_table.create_record(*test_data_2)

        self.assertEqual(str(context.exception), error_message)
        
        # Проверяем, что вторая запись не добавлена
        all_records = self.student_table.select_record()
        self.assertEqual(len(all_records), 1)
        self.assertEqual(all_records[0], test_data_1)

    def test_create_record_empty_strings(self):
        """Тест создания с пустыми строками"""
        record = self.student_table.create_record(1, "", "", 20, "")
        expected = (1, "", "", 20, "")
        self.assertEqual(record, expected)

    # ============= ТЕСТЫ ДЛЯ select_record =============
    
    def test_select_record_empty_table(self):
        """Тест выборки из пустой таблицы"""
        records = self.student_table.select_record()
        self.assertEqual(records, [])
        
        records_with_filter = self.student_table.select_record(student_id=1)
        self.assertEqual(records_with_filter, [])

    def test_select_record_no_filters(self):
        """Тест выборки без фильтров"""
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
        ]
        
        for test_data in test_datas:
            self.student_table.create_record(*test_data)
            
        records = self.student_table.select_record()
        self.assertEqual(records, test_datas)
        
        # Проверяем, что возвращается копия, а не оригинал
        records.append((4, "Extra", "Person", 25, "M"))
        self.assertNotEqual(self.student_table.select_record(), records)

    def test_select_record_by_id(self):
        """Тест фильтрации по ID"""
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
        ]
        
        for test_data in test_datas:
            self.student_table.create_record(*test_data)
            
        # Существующий ID
        records = self.student_table.select_record(student_id=2)
        self.assertEqual(records, [test_datas[1]])
        
        # Несуществующий ID
        records = self.student_table.select_record(student_id=99)
        self.assertEqual(records, [])

    def test_select_record_by_first_name(self):
        """Тест фильтрации по имени"""
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "John", "Johnson", 19, "M"),
            (4, "Bob", "Brown", 21, "M"),
        ]
        
        for test_data in test_datas:
            self.student_table.create_record(*test_data)
            
        records = self.student_table.select_record(first_name="John")
        self.assertEqual(records, [test_datas[0], test_datas[2]])
        
        # Несуществующее имя
        records = self.student_table.select_record(first_name="Nonexistent")
        self.assertEqual(records, [])

    def test_select_record_by_second_name(self):
        """Тест фильтрации по фамилии"""
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Doe", 19, "F"),
        ]
        
        for test_data in test_datas:
            self.student_table.create_record(*test_data)
            
        records = self.student_table.select_record(second_name="Doe")
        self.assertEqual(records, [test_datas[0], test_datas[2]])

    def test_select_record_by_age(self):
        """Тест фильтрации по возрасту"""
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 20, "F"),
            (3, "Alice", "Johnson", 21, "F"),
            (4, "Bob", "Brown", 20, "M"),
        ]
        
        for test_data in test_datas:
            self.student_table.create_record(*test_data)
            
        records = self.student_table.select_record(age=20)
        self.assertEqual(records, [test_datas[0], test_datas[1], test_datas[3]])

    def test_select_record_by_sex(self):
        """Тест фильтрации по полу"""
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
            (4, "Bob", "Brown", 21, "M"),
            (5, "Charlie", "Davis", 18, "M"),
        ]
        
        for test_data in test_datas:
            self.student_table.create_record(*test_data)
            
        records_male = self.student_table.select_record(sex="M")
        expected_male = [test_datas[0], test_datas[3], test_datas[4]]
        self.assertEqual(records_male, expected_male)
        
        records_female = self.student_table.select_record(sex="F")
        expected_female = [test_datas[1], test_datas[2]]
        self.assertEqual(records_female, expected_female)

    def test_select_record_multiple_filters(self):
        """Тест фильтрации по нескольким критериям"""
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "John", "Smith", 25, "M"),
            (3, "John", "Doe", 30, "M"),
            (4, "Jane", "Doe", 20, "F"),
        ]
        
        for test_data in test_datas:
            self.student_table.create_record(*test_data)
            
        # Комбинированный фильтр
        records = self.student_table.select_record(
            first_name="John",
            second_name="Doe",
            age=20,
            sex="M"
        )
        self.assertEqual(records, [test_datas[0]])
        
        # Фильтр с частичным совпадением
        records = self.student_table.select_record(
            first_name="John",
            second_name="Doe"
        )
        self.assertEqual(records, [test_datas[0], test_datas[2]])

    def test_select_record_preserves_order(self):
        """Тест сохранения порядка записей"""
        test_datas = [
            (3, "Charlie", "Davis", 18, "M"),
            (1, "Alice", "Johnson", 19, "F"),
            (2, "Bob", "Brown", 21, "M"),
        ]
        
        for test_data in test_datas:
            self.student_table.create_record(*test_data)
            
        records = self.student_table.select_record()
        # Порядок должен соответствовать порядку добавления
        self.assertEqual(records, test_datas)

    # ============= ТЕСТЫ ДЛЯ update_record =============
    
    def test_update_record_success(self):
        """Тест успешного обновления записи"""
        # Подготовка
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        
        cases = [
            {
                "name": "Обновление имени",
                "new_data": (1, "Jonathan", "Doe", 20, "M"),
                "expected": (1, "Jonathan", "Doe", 20, "M"),
            },
            {
                "name": "Обновление фамилии",
                "new_data": (1, "John", "Johnson", 20, "M"),
                "expected": (1, "John", "Johnson", 20, "M"),
            },
            {
                "name": "Обновление возраста",
                "new_data": (1, "John", "Doe", 25, "M"),
                "expected": (1, "John", "Doe", 25, "M"),
            },
            {
                "name": "Обновление пола",
                "new_data": (1, "John", "Doe", 20, "F"),
                "expected": (1, "John", "Doe", 20, "F"),
            },
            {
                "name": "Обновление всех полей",
                "new_data": (1, "Jonathan", "Johnson", 30, "F"),
                "expected": (1, "Jonathan", "Johnson", 30, "F"),
            },
        ]
        
        for case in cases:
            with self.subTest(case=case["name"]):
                # Сбрасываем состояние
                self.student_table = StudentTable()
                self.student_table.create_record(1, "John", "Doe", 20, "M")
                
                updated = self.student_table.update_record(*case["new_data"])
                self.assertEqual(updated, case["expected"])
                
                # Проверяем в таблице
                selected = self.student_table.select_record(student_id=1)
                self.assertEqual(selected[0], case["expected"])

    def test_update_record_strip_whitespace(self):
        """Тест удаления пробелов при обновлении"""
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        
        new_data = (1, "  Jonathan  ", "  Johnson  ", 25, "  F  ")
        expected = (1, "Jonathan", "Johnson", 25, "F")
        
        updated = self.student_table.update_record(*new_data)
        self.assertEqual(updated, expected)
        
        selected = self.student_table.select_record(student_id=1)
        self.assertEqual(selected[0], expected)

    def test_update_record_not_found(self):
        """Тест обновления несуществующей записи"""
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        
        new_data = (99, "Nonexistent", "Student", 20, "M")
        
        with self.assertRaises(KeyError) as context:
            self.student_table.update_record(*new_data)
        
        self.assertIn("99", str(context.exception))
        self.assertIn("не найдена", str(context.exception))

    def test_update_record_negative_age(self):
        """Тест обновления с отрицательным возрастом"""
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        
        new_data = (1, "John", "Doe", -5, "M")
        
        with self.assertRaises(InvalidAgeError) as context:
            self.student_table.update_record(*new_data)
        
        self.assertEqual(str(context.exception), "Поле age не может быть отрицательным.")
        
        # Проверяем, что запись не изменилась
        original = self.student_table.select_record(student_id=1)
        self.assertEqual(original[0], (1, "John", "Doe", 20, "M"))

    def test_update_record_multiple_updates(self):
        """Тест множественного обновления одной записи"""
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        
        # Первое обновление
        self.student_table.update_record(1, "Jonathan", "Doe", 20, "M")
        
        # Второе обновление
        updated = self.student_table.update_record(1, "Jonathan", "Doe", 25, "M")
        self.assertEqual(updated, (1, "Jonathan", "Doe", 25, "M"))
        
        # Проверяем конечный результат
        selected = self.student_table.select_record(student_id=1)
        self.assertEqual(selected[0], (1, "Jonathan", "Doe", 25, "M"))

    def test_update_record_preserves_other_records(self):
        """Тест сохранения других записей при обновлении"""
        records = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Bob", "Brown", 21, "M"),
        ]
        
        for record in records:
            self.student_table.create_record(*record)
            
        # Обновляем только первую запись
        self.student_table.update_record(1, "Jonathan", "Doe", 20, "M")
        
        all_records = self.student_table.select_record()
        expected = [
            (1, "Jonathan", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Bob", "Brown", 21, "M"),
        ]
        self.assertEqual(all_records, expected)

    # ============= ТЕСТЫ ДЛЯ delete_record =============
    
    def test_delete_record_success(self):
        """Тест успешного удаления записи"""
        records = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
            (4, "Bob", "Brown", 21, "M"),
            (5, "Charlie", "Davis", 18, "M"),
        ]
        
        for record in records:
            self.student_table.create_record(*record)
        
        # Удаляем запись из середины
        deleted = self.student_table.delete_record(3)
        self.assertEqual(deleted, (3, "Alice", "Johnson", 19, "F"))
        
        # Проверяем, что запись удалена
        remaining = self.student_table.select_record(student_id=3)
        self.assertEqual(remaining, [])
        
        # Проверяем остальные записи
        all_records = self.student_table.select_record()
        expected = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (4, "Bob", "Brown", 21, "M"),
            (5, "Charlie", "Davis", 18, "M"),
        ]
        self.assertEqual(all_records, expected)

    def test_delete_record_first(self):
        """Тест удаления первой записи"""
        records = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Bob", "Brown", 21, "M"),
        ]
        
        for record in records:
            self.student_table.create_record(*record)
            
        deleted = self.student_table.delete_record(1)
        self.assertEqual(deleted, (1, "John", "Doe", 20, "M"))
        
        all_records = self.student_table.select_record()
        expected = [
            (2, "Jane", "Smith", 22, "F"),
            (3, "Bob", "Brown", 21, "M"),
        ]
        self.assertEqual(all_records, expected)

    def test_delete_record_last(self):
        """Тест удаления последней записи"""
        records = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Bob", "Brown", 21, "M"),
        ]
        
        for record in records:
            self.student_table.create_record(*record)
            
        deleted = self.student_table.delete_record(3)
        self.assertEqual(deleted, (3, "Bob", "Brown", 21, "M"))
        
        all_records = self.student_table.select_record()
        expected = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
        ]
        self.assertEqual(all_records, expected)

    def test_delete_record_not_found(self):
        """Тест удаления несуществующей записи"""
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        
        with self.assertRaises(KeyError) as context:
            self.student_table.delete_record(999)
        
        self.assertIn("999", str(context.exception))
        self.assertIn("не найдена", str(context.exception))
        
        # Проверяем, что таблица не изменилась
        all_records = self.student_table.select_record()
        self.assertEqual(len(all_records), 1)

    def test_delete_record_consecutive(self):
        """Тест последовательного удаления нескольких записей"""
        records = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
            (4, "Bob", "Brown", 21, "M"),
            (5, "Charlie", "Davis", 18, "M"),
        ]
        
        for record in records:
            self.student_table.create_record(*record)
        
        # Удаляем три записи
        self.student_table.delete_record(2)
        self.student_table.delete_record(4)
        self.student_table.delete_record(1)
        
        remaining = self.student_table.select_record()
        expected = [
            (3, "Alice", "Johnson", 19, "F"),
            (5, "Charlie", "Davis", 18, "M"),
        ]
        self.assertEqual(remaining, expected)
        
        # Удаляем оставшиеся
        self.student_table.delete_record(3)
        self.student_table.delete_record(5)
        self.assertEqual(self.student_table.select_record(), [])

    def test_delete_record_empty_table(self):
        """Тест удаления из пустой таблицы"""
        with self.assertRaises(KeyError) as context:
            self.student_table.delete_record(1)
        
        self.assertIn("1", str(context.exception))

    # ============= ИНТЕГРАЦИОННЫЕ ТЕСТЫ =============
    
    def test_full_crud_workflow(self):
        """Полный цикл CRUD операций"""
        # CREATE
        record1 = self.student_table.create_record(1, "John", "Doe", 20, "M")
        record2 = self.student_table.create_record(2, "Jane", "Smith", 22, "F")
        self.assertEqual(len(self.student_table.select_record()), 2)
        
        # READ
        selected = self.student_table.select_record(first_name="John")
        self.assertEqual(selected, [record1])
        
        # UPDATE
        updated = self.student_table.update_record(1, "Jonathan", "Doe", 21, "M")
        self.assertEqual(updated, (1, "Jonathan", "Doe", 21, "M"))
        
        # Проверяем обновление
        selected = self.student_table.select_record(student_id=1)
        self.assertEqual(selected[0], (1, "Jonathan", "Doe", 21, "M"))
        
        # DELETE
        deleted = self.student_table.delete_record(2)
        self.assertEqual(deleted, record2)
        
        # Финальная проверка
        final = self.student_table.select_record()
        self.assertEqual(final, [(1, "Jonathan", "Doe", 21, "M")])

    def test_data_integrity_after_operations(self):
        """Проверка целостности данных после операций"""
        # Создаем несколько записей
        for i in range(1, 6):
            self.student_table.create_record(i, f"Name{i}", f"Last{i}", 20 + i, "M")
        
        # Обновляем одну запись
        self.student_table.update_record(3, "Updated", "Name", 25, "F")
        
        # Удаляем другую
        self.student_table.delete_record(2)
        
        # Проверяем, что остальные записи не изменились
        records = self.student_table.select_record()
        expected = [
            (1, "Name1", "Last1", 21, "M"),
            (3, "Updated", "Name", 25, "F"),
            (4, "Name4", "Last4", 24, "M"),
            (5, "Name5", "Last5", 25, "M"),
        ]
        self.assertEqual(records, expected)
        
        # Проверяем, что можно создать запись с удаленным ID
        new_record = self.student_table.create_record(2, "New", "Record", 30, "F")
        self.assertEqual(new_record, (2, "New", "Record", 30, "F"))


if __name__ == "__main__":
    unittest.main()