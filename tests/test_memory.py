import unittest
from src.db.backend.memory import StudentTable
from src.db.backend.errors import InvalidAgeError, DuplicateIDError


class TestMemory(unittest.TestCase):
    def setUp(self):
        self.student_table = StudentTable()
        self.assertIsInstance(self.student_table, StudentTable)

    def test_create_record_success(self):
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

        all_records = self.student_table.select_record()
        self.assertEqual(len(all_records), 12)

    def test_create_record_strip_whitespace(self):
        test_data = (1, "  John  ", "  Doe  ", 20, "  M  ")
        expected = (1, "John", "Doe", 20, "M")

        record = self.student_table.create_record(*test_data)
        self.assertEqual(record, expected)

        selected = self.student_table.select_record(student_id=1)
        self.assertEqual(selected[0], expected)

    def test_create_record_negative_age(self):
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

        self.assertEqual(len(self.student_table.select_record()), 0)

    def test_create_record_zero_age(self):
        record = self.student_table.create_record(1, "John", "Doe", 0, "M")
        self.assertEqual(record, (1, "John", "Doe", 0, "M"))

    def test_create_record_duplicate_id(self):
        test_data_1 = (1, "John", "Doe", 20, "M")
        test_data_2 = (1, "Jane", "Smith", 22, "F")
        error_message = "Запись с id=1 уже существует."

        self.student_table.create_record(*test_data_1)

        with self.assertRaises(DuplicateIDError) as context:
            self.student_table.create_record(*test_data_2)

        self.assertEqual(str(context.exception), error_message)

        all_records = self.student_table.select_record()
        self.assertEqual(len(all_records), 1)
        self.assertEqual(all_records[0], test_data_1)

    def test_create_record_empty_strings(self):
        record = self.student_table.create_record(1, "", "", 20, "")
        expected = (1, "", "", 20, "")
        self.assertEqual(record, expected)

    def test_select_record_empty_table(self):
        records = self.student_table.select_record()
        self.assertEqual(records, [])

        records_with_filter = self.student_table.select_record(student_id=1)
        self.assertEqual(records_with_filter, [])

    def test_select_record_no_filters(self):
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
        ]

        for test_data in test_datas:
            self.student_table.create_record(*test_data)

        records = self.student_table.select_record()
        self.assertEqual(records, test_datas)

        records.append((4, "Extra", "Person", 25, "M"))
        self.assertNotEqual(self.student_table.select_record(), records)

    def test_select_record_by_id(self):
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "Jane", "Smith", 22, "F"),
            (3, "Alice", "Johnson", 19, "F"),
        ]

        for test_data in test_datas:
            self.student_table.create_record(*test_data)

        records = self.student_table.select_record(student_id=2)
        self.assertEqual(records, [test_datas[1]])

        records = self.student_table.select_record(student_id=99)
        self.assertEqual(records, [])

    def test_select_record_by_first_name(self):
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

        records = self.student_table.select_record(first_name="Nonexistent")
        self.assertEqual(records, [])

    def test_select_record_by_second_name(self):
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
        test_datas = [
            (1, "John", "Doe", 20, "M"),
            (2, "John", "Smith", 25, "M"),
            (3, "John", "Doe", 30, "M"),
            (4, "Jane", "Doe", 20, "F"),
        ]

        for test_data in test_datas:
            self.student_table.create_record(*test_data)

        records = self.student_table.select_record(
            first_name="John",
            second_name="Doe",
            age=20,
            sex="M"
        )
        self.assertEqual(records, [test_datas[0]])

        records = self.student_table.select_record(
            first_name="John",
            second_name="Doe"
        )
        self.assertEqual(records, [test_datas[0], test_datas[2]])

    def test_select_record_preserves_order(self):
        test_datas = [
            (3, "Charlie", "Davis", 18, "M"),
            (1, "Alice", "Johnson", 19, "F"),
            (2, "Bob", "Brown", 21, "M"),
        ]

        for test_data in test_datas:
            self.student_table.create_record(*test_data)

        records = self.student_table.select_record()
        self.assertEqual(records, test_datas)

    def test_update_record_success(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")

        cases = [
            {"name": "Обновление имени", "new_data": (1, "Jonathan", "Doe", 20, "M"), "expected": (1, "Jonathan", "Doe", 20, "M")},
            {"name": "Обновление фамилии", "new_data": (1, "John", "Johnson", 20, "M"), "expected": (1, "John", "Johnson", 20, "M")},
            {"name": "Обновление возраста", "new_data": (1, "John", "Doe", 25, "M"), "expected": (1, "John", "Doe", 25, "M")},
            {"name": "Обновление пола", "new_data": (1, "John", "Doe", 20, "F"), "expected": (1, "John", "Doe", 20, "F")},
            {"name": "Обновление всех полей", "new_data": (1, "Jonathan", "Johnson", 30, "F"), "expected": (1, "Jonathan", "Johnson", 30, "F")},
        ]

        for case in cases:
            with self.subTest(case=case["name"]):
                self.student_table = StudentTable()
                self.student_table.create_record(1, "John", "Doe", 20, "M")
                updated = self.student_table.update_record(*case["new_data"])
                self.assertEqual(updated, case["expected"])
                selected = self.student_table.select_record(student_id=1)
                self.assertEqual(selected[0], case["expected"])

    def test_update_record_strip_whitespace(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        new_data = (1, "  Jonathan  ", "  Johnson  ", 25, "  F  ")
        expected = (1, "Jonathan", "Johnson", 25, "F")
        updated = self.student_table.update_record(*new_data)
        self.assertEqual(updated, expected)
        selected = self.student_table.select_record(student_id=1)
        self.assertEqual(selected[0], expected)

    def test_update_record_not_found(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        new_data = (99, "Nonexistent", "Student", 20, "M")
        with self.assertRaises(KeyError) as context:
            self.student_table.update_record(*new_data)
        self.assertIn("99", str(context.exception))

    def test_update_record_negative_age(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        new_data = (1, "John", "Doe", -5, "M")
        with self.assertRaises(InvalidAgeError):
            self.student_table.update_record(*new_data)
        original = self.student_table.select_record(student_id=1)
        self.assertEqual(original[0], (1, "John", "Doe", 20, "M"))

    def test_update_record_multiple_updates(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        self.student_table.update_record(1, "Jonathan", "Doe", 20, "M")
        updated = self.student_table.update_record(1, "Jonathan", "Doe", 25, "M")
        self.assertEqual(updated, (1, "Jonathan", "Doe", 25, "M"))
        selected = self.student_table.select_record(student_id=1)
        self.assertEqual(selected[0], (1, "Jonathan", "Doe", 25, "M"))

    def test_update_record_preserves_other_records(self):
        records = [(1, "John", "Doe", 20, "M"), (2, "Jane", "Smith", 22, "F"), (3, "Bob", "Brown", 21, "M")]
        for record in records:
            self.student_table.create_record(*record)
        self.student_table.update_record(1, "Jonathan", "Doe", 20, "M")
        all_records = self.student_table.select_record()
        expected = [(1, "Jonathan", "Doe", 20, "M"), (2, "Jane", "Smith", 22, "F"), (3, "Bob", "Brown", 21, "M")]
        self.assertEqual(all_records, expected)

    def test_delete_record_success(self):
        records = [(1, "John", "Doe", 20, "M"), (2, "Jane", "Smith", 22, "F"), (3, "Alice", "Johnson", 19, "F"), (4, "Bob", "Brown", 21, "M"), (5, "Charlie", "Davis", 18, "M")]
        for record in records:
            self.student_table.create_record(*record)
        deleted = self.student_table.delete_record(3)
        self.assertEqual(deleted, (3, "Alice", "Johnson", 19, "F"))
        all_records = self.student_table.select_record()
        expected = [(1, "John", "Doe", 20, "M"), (2, "Jane", "Smith", 22, "F"), (4, "Bob", "Brown", 21, "M"), (5, "Charlie", "Davis", 18, "M")]
        self.assertEqual(all_records, expected)

    def test_delete_record_first(self):
        records = [(1, "John", "Doe", 20, "M"), (2, "Jane", "Smith", 22, "F"), (3, "Bob", "Brown", 21, "M")]
        for record in records:
            self.student_table.create_record(*record)
        deleted = self.student_table.delete_record(1)
        self.assertEqual(deleted, (1, "John", "Doe", 20, "M"))
        all_records = self.student_table.select_record()
        expected = [(2, "Jane", "Smith", 22, "F"), (3, "Bob", "Brown", 21, "M")]
        self.assertEqual(all_records, expected)

    def test_delete_record_last(self):
        records = [(1, "John", "Doe", 20, "M"), (2, "Jane", "Smith", 22, "F"), (3, "Bob", "Brown", 21, "M")]
        for record in records:
            self.student_table.create_record(*record)
        deleted = self.student_table.delete_record(3)
        self.assertEqual(deleted, (3, "Bob", "Brown", 21, "M"))
        all_records = self.student_table.select_record()
        expected = [(1, "John", "Doe", 20, "M"), (2, "Jane", "Smith", 22, "F")]
        self.assertEqual(all_records, expected)

    def test_delete_record_not_found(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        with self.assertRaises(KeyError) as context:
            self.student_table.delete_record(999)
        self.assertIn("999", str(context.exception))

    def test_delete_record_consecutive(self):
        records = [(1, "John", "Doe", 20, "M"), (2, "Jane", "Smith", 22, "F"), (3, "Alice", "Johnson", 19, "F"), (4, "Bob", "Brown", 21, "M"), (5, "Charlie", "Davis", 18, "M")]
        for record in records:
            self.student_table.create_record(*record)
        self.student_table.delete_record(2)
        self.student_table.delete_record(4)
        self.student_table.delete_record(1)
        remaining = self.student_table.select_record()
        expected = [(3, "Alice", "Johnson", 19, "F"), (5, "Charlie", "Davis", 18, "M")]
        self.assertEqual(remaining, expected)

    def test_delete_record_empty_table(self):
        with self.assertRaises(KeyError):
            self.student_table.delete_record(1)

    def test_full_crud_workflow(self):
        record1 = self.student_table.create_record(1, "John", "Doe", 20, "M")
        record2 = self.student_table.create_record(2, "Jane", "Smith", 22, "F")
        self.assertEqual(len(self.student_table.select_record()), 2)
        selected = self.student_table.select_record(first_name="John")
        self.assertEqual(selected, [record1])
        updated = self.student_table.update_record(1, "Jonathan", "Doe", 21, "M")
        self.assertEqual(updated, (1, "Jonathan", "Doe", 21, "M"))
        selected = self.student_table.select_record(student_id=1)
        self.assertEqual(selected[0], (1, "Jonathan", "Doe", 21, "M"))
        deleted = self.student_table.delete_record(2)
        self.assertEqual(deleted, record2)
        final = self.student_table.select_record()
        self.assertEqual(final, [(1, "Jonathan", "Doe", 21, "M")])

    def test_sort_records_by_id_ascending(self):
        self.student_table.create_record(3, "John", "Doe", 20, "M")
        self.student_table.create_record(1, "Jane", "Smith", 22, "F")
        self.student_table.create_record(2, "Bob", "Brown", 21, "M")
        sorted_records = self.student_table.sort_records("student_id", reverse=False)
        expected = [(1, "Jane", "Smith", 22, "F"), (2, "Bob", "Brown", 21, "M"), (3, "John", "Doe", 20, "M")]
        self.assertEqual(sorted_records, expected)

    def test_sort_records_by_id_descending(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        self.student_table.create_record(3, "Jane", "Smith", 22, "F")
        self.student_table.create_record(2, "Bob", "Brown", 21, "M")
        sorted_records = self.student_table.sort_records("student_id", reverse=True)
        expected = [(3, "Jane", "Smith", 22, "F"), (2, "Bob", "Brown", 21, "M"), (1, "John", "Doe", 20, "M")]
        self.assertEqual(sorted_records, expected)

    def test_sort_records_by_age_ascending(self):
        self.student_table.create_record(1, "John", "Doe", 25, "M")
        self.student_table.create_record(2, "Jane", "Smith", 20, "F")
        self.student_table.create_record(3, "Bob", "Brown", 22, "M")
        sorted_records = self.student_table.sort_records("age", reverse=False)
        expected = [(2, "Jane", "Smith", 20, "F"), (3, "Bob", "Brown", 22, "M"), (1, "John", "Doe", 25, "M")]
        self.assertEqual(sorted_records, expected)

    def test_sort_records_by_first_name(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        self.student_table.create_record(2, "Alice", "Smith", 22, "F")
        self.student_table.create_record(3, "Bob", "Brown", 21, "M")
        sorted_records = self.student_table.sort_records("first_name", reverse=False)
        expected = [(2, "Alice", "Smith", 22, "F"), (3, "Bob", "Brown", 21, "M"), (1, "John", "Doe", 20, "M")]
        self.assertEqual(sorted_records, expected)

    def test_sort_records_by_second_name(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        self.student_table.create_record(2, "Jane", "Smith", 22, "F")
        self.student_table.create_record(3, "Bob", "Brown", 21, "M")
        sorted_records = self.student_table.sort_records("second_name", reverse=False)
        expected = [(3, "Bob", "Brown", 21, "M"), (1, "John", "Doe", 20, "M"), (2, "Jane", "Smith", 22, "F")]
        self.assertEqual(sorted_records, expected)

    def test_sort_records_by_sex(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        self.student_table.create_record(2, "Jane", "Smith", 22, "F")
        self.student_table.create_record(3, "Bob", "Brown", 21, "M")
        sorted_records = self.student_table.sort_records("sex", reverse=False)
        expected = [(2, "Jane", "Smith", 22, "F"), (1, "John", "Doe", 20, "M"), (3, "Bob", "Brown", 21, "M")]
        self.assertEqual(sorted_records, expected)

    def test_sort_records_empty_table(self):
        sorted_records = self.student_table.sort_records("student_id")
        self.assertEqual(sorted_records, [])

    def test_sort_records_invalid_field(self):
        self.student_table.create_record(1, "John", "Doe", 20, "M")
        with self.assertRaises(ValueError):
            self.student_table.sort_records("invalid_field")

    def test_sort_records_original_unchanged(self):
        self.student_table.create_record(3, "John", "Doe", 20, "M")
        self.student_table.create_record(1, "Jane", "Smith", 22, "F")
        original = self.student_table.select_record()
        self.student_table.sort_records("student_id")
        self.assertEqual(self.student_table.select_record(), original)


if __name__ == "__main__":
    unittest.main()