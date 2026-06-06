from src.db.backend.memory import MemoryDatabase
from src.db.backend.file_json import JSONDatabase
from src.db.backend.file_csv import CSVDatabase
from src.db.backend.errors import TableNotFoundError, MissingColumnError, UnknownColumnError, DuplicateIDError, InvalidAgeError


class StudentTUI:
    def __init__(self):
        self.database = None
        self.running = True
        self._select_database_type()

    def _select_database_type(self):
        print("\n=== ВЫБОР ТИПА БАЗЫ ДАННЫХ ===")
        print("1. In-memory (данные не сохраняются)")
        print("2. File (JSON) - данные сохраняются в JSON файлы")
        print("3. File (CSV) - данные сохраняются в CSV файлы")

        choice = input("Выберите тип (1-3): ").strip()

        if choice == "2":
            self.database = JSONDatabase()
            print("Используется файловая база данных (JSON, папка 'data/')")
        elif choice == "3":
            self.database = CSVDatabase()
            print("Используется файловая база данных (CSV, папка 'data_csv/')")
        else:
            self.database = MemoryDatabase()
            print("Используется in-memory база данных")

    def _ensure_table_exists(self):
        try:
            self.database.select_records("students")
        except TableNotFoundError:
            self.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
            print("Таблица 'students' создана.")

    def print_menu(self):
        print("\n=== БАЗА ДАННЫХ СТУДЕНТОВ ===")
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Найти записи по фильтру")
        print("4. Обновить запись")
        print("5. Удалить запись")
        print("6. Сортировать записи")
        print("7. Показать информацию о БД")
        print("0. Выход")

    def _read_int(self, prompt: str) -> int:
        while True:
            raw = input(prompt).strip()
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число.")

    def _read_optional_int(self, prompt: str) -> int | None:
        while True:
            raw = input(prompt).strip()
            if raw == "":
                return None
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число или оставьте поле пустым.")

    def _print_records(self, records: list):
        if not records:
            print("Записи не найдены.")
            return
        for record in records:
            print(f"ID: {record['student_id']} | {record['first_name']} {record['second_name']} | "
                  f"Возраст: {record['age']} | Пол: {record['sex']}")

    def add_student(self):
        self._ensure_table_exists()
        print("\nДобавление записи")

        student_id = self._read_int("ID: ")
        first_name = input("Имя: ").strip()
        second_name = input("Фамилия: ").strip()
        age = self._read_int("Возраст: ")
        sex = input("Пол (M/F): ").strip().upper()

        if age < 0:
            print("Ошибка: возраст не может быть отрицательным.")
            return

        try:
            record = {
                "student_id": student_id,
                "first_name": first_name,
                "second_name": second_name,
                "age": age,
                "sex": sex
            }
            self.database.insert_record("students", record)
            print(f"Запись добавлена: {record}")
        except (DuplicateIDError, MissingColumnError, UnknownColumnError, InvalidAgeError) as exc:
            print(f"Ошибка: {exc}")

    def show_all_students(self):
        try:
            self._ensure_table_exists()
            records = self.database.select_records("students")
            print("\n=== СПИСОК СТУДЕНТОВ ===")
            self._print_records(records)
        except TableNotFoundError:
            print("Таблица не найдена. Сначала добавьте записи.")

    def find_students(self):
        try:
            self._ensure_table_exists()
            print("\nПоиск по фильтру (Enter = пропустить поле)")
            filters = {}

            student_id = self._read_optional_int("ID: ")
            if student_id is not None:
                filters["student_id"] = student_id

            first_name = input("Имя: ").strip()
            if first_name:
                filters["first_name"] = first_name

            second_name = input("Фамилия: ").strip()
            if second_name:
                filters["second_name"] = second_name

            age = self._read_optional_int("Возраст: ")
            if age is not None:
                filters["age"] = age

            sex = input("Пол (M/F): ").strip().upper()
            if sex:
                filters["sex"] = sex

            records = self.database.select_records("students", **filters)
            print("\n=== РЕЗУЛЬТАТЫ ПОИСКА ===")
            self._print_records(records)
        except TableNotFoundError:
            print("Таблица не найдена. Сначала добавьте записи.")

    def update_student(self):
        try:
            self._ensure_table_exists()
            student_id = self._read_int("Введите ID студента для обновления: ")

            existing = self.database.select_records("students", student_id=student_id)
            if not existing:
                print(f"Студент с ID {student_id} не найден.")
                return

            current = existing[0]
            print(f"Текущие данные: ID: {current['student_id']} | {current['first_name']} {current['second_name']} | "
                  f"Возраст: {current['age']} | Пол: {current['sex']}")

            updates = {"student_id": student_id}

            first_name = input(f"Новое имя ({current['first_name']}): ").strip()
            if first_name:
                updates["first_name"] = first_name

            second_name = input(f"Новая фамилия ({current['second_name']}): ").strip()
            if second_name:
                updates["second_name"] = second_name

            age_input = input(f"Новый возраст ({current['age']}): ").strip()
            if age_input:
                try:
                    age = int(age_input)
                    if age < 0:
                        print("Ошибка: возраст не может быть отрицательным.")
                        return
                    updates["age"] = age
                except ValueError:
                    print("Ошибка: введите целое число.")

            sex = input(f"Новый пол ({current['sex']}): ").strip().upper()
            if sex:
                updates["sex"] = sex

            if self.database.update_record("students", **updates):
                print("Запись успешно обновлена!")
            else:
                print("Запись не найдена.")
        except TableNotFoundError:
            print("Таблица не найдена.")

    def delete_student(self):
        try:
            self._ensure_table_exists()
            student_id = self._read_int("Введите ID студента для удаления: ")

            if self.database.delete_record("students", student_id):
                print(f"Студент с ID {student_id} успешно удален!")
            else:
                print(f"Студент с ID {student_id} не найден.")
        except TableNotFoundError:
            print("Таблица не найдена.")

    def sort_students(self):
        try:
            self._ensure_table_exists()
            records = self.database.select_records("students")
            if not records:
                print("Нет записей для сортировки.")
                return
            
            print("\n=== Сортировка записей ===")
            print("Поля для сортировки:")
            print("1. По ID (student_id)")
            print("2. По имени (first_name)")
            print("3. По фамилии (second_name)")
            print("4. По возрасту (age)")
            print("5. По полу (sex)")
            
            field_choice = input("Выберите поле (1-5): ").strip()
            
            field_map = {
                "1": "student_id",
                "2": "first_name",
                "3": "second_name",
                "4": "age",
                "5": "sex"
            }
            
            if field_choice not in field_map:
                print("Ошибка: неверный выбор поля.")
                return
            
            field = field_map[field_choice]
            
            print("\nПорядок сортировки:")
            print("1. По возрастанию")
            print("2. По убыванию")
            
            order_choice = input("Выберите порядок (1-2): ").strip()
            
            if order_choice not in ["1", "2"]:
                print("Ошибка: неверный выбор порядка.")
                return
            
            reverse = (order_choice == "2")
            
            sorted_records = sorted(records, key=lambda x: x[field], reverse=reverse)
            
            order_str = "убыванию" if reverse else "возрастанию"
            print(f"\n=== Отсортировано по {field} ({order_str}) ===")
            
            for record in sorted_records:
                print(f"ID: {record['student_id']} | {record['first_name']} {record['second_name']} | "
                      f"Возраст: {record['age']} | Пол: {record['sex']}")
        except TableNotFoundError:
            print("Таблица не найдена.")

    def show_info(self):
        print("\n=== ИНФОРМАЦИЯ О БАЗЕ ДАННЫХ ===")
        db_type = type(self.database).__name__
        if db_type == "MemoryDatabase":
            print("Тип: In-memory база данных")
            print("Данные не сохраняются между запусками")
        elif db_type == "JSONDatabase":
            print("Тип: Файловая база данных (JSON)")
            print("Папка хранения: data/")
        else:
            print("Тип: Файловая база данных (CSV)")
            print("Папка хранения: data_csv/")

        try:
            self._ensure_table_exists()
            records = self.database.select_records("students")
            print(f"Количество записей: {len(records)}")
        except TableNotFoundError:
            print("Таблица ещё не создана")

    def run(self):
        while self.running:
            self.print_menu()
            action = input("Выберите действие: ").strip()

            if action == "1":
                self.add_student()
            elif action == "2":
                self.show_all_students()
            elif action == "3":
                self.find_students()
            elif action == "4":
                self.update_student()
            elif action == "5":
                self.delete_student()
            elif action == "6":
                self.sort_students()
            elif action == "7":
                self.show_info()
            elif action == "0":
                print("До свидания!")
                self.running = False
            else:
                print("Неверный выбор. Попробуйте снова.")


def run():
    app = StudentTUI()
    app.run()