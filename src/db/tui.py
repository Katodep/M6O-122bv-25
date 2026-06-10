from .backend.memory import StudentTable
from .backend.file_csv import CSVDatabase
from .backend.file_json import JSONDatabase


class StudentTUI:
    def __init__(self):
        print("Выберите тип базы данных:")
        print("1. In-memory")
        print("2. JSON файлы")
        print("3. CSV файлы")
        choice = input("Выберите (1-3): ").strip()
        
        if choice == "1":
            self.database = StudentTable()
            print("Используется in-memory база данных")
        elif choice == "2":
            self.database = JSONDatabase()
            print("Используется JSON база данных")
        elif choice == "3":
            self.database = CSVDatabase()
            print("Используется CSV база данных")
        else:
            self.database = StudentTable()
            print("Используется in-memory база данных")
        
        self.running = True
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        try:
            self.database.select_records("students")
        except:
            self.database.create_table("students", ("student_id", "first_name", "second_name", "age", "sex"))
    
    def print_menu(self):
        print("\n=== База студентов ===")
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Найти записи по фильтру")
        print("4. Обновить запись")
        print("5. Удалить по id")
        print("6. Сортировать записи")
        print("0. Выход")
    
    def _read_int(self, prompt):
        while True:
            try:
                return int(input(prompt).strip())
            except ValueError:
                print("Ошибка: введите целое число.")
    
    def _read_optional_int(self, prompt):
        while True:
            raw = input(prompt).strip()
            if raw == "":
                return None
            try:
                return int(raw)
            except ValueError:
                print("Ошибка: введите целое число или оставьте поле пустым.")
    
    def _print_records(self, records):
        if not records:
            print("Записи не найдены.")
            return
        for record in records:
            print(record)
    
    def add_student(self):
        print("\nДобавление записи")
        student_id = self._read_int("id (0 - авто): ")
        if student_id == 0:
            student_id = None
        
        first_name = input("first_name: ").strip()
        second_name = input("second_name: ").strip()
        age = self._read_int("age: ")
        sex = input("sex: ").strip()
        
        try:
            record = self.database.create_record(
                student_id=student_id,
                first_name=first_name,
                second_name=second_name,
                age=age,
                sex=sex
            )
            print(f"Запись добавлена: {record}")
        except Exception as exc:
            print(f"Ошибка: {exc}")
    
    def show_all_students(self):
        print("\nСписок записей")
        records = self.database.select_records("students")
        self._print_records(records)
    
    def find_students(self):
        print("\nПоиск по фильтру (Enter = пропустить поле)")
        filters = {}
        
        student_id = self._read_optional_int("id: ")
        if student_id is not None:
            filters['student_id'] = student_id
        
        first_name = input("first_name: ").strip()
        if first_name:
            filters['first_name'] = first_name
        
        second_name = input("second_name: ").strip()
        if second_name:
            filters['second_name'] = second_name
        
        age = self._read_optional_int("age: ")
        if age is not None:
            filters['age'] = age
        
        sex = input("sex: ").strip()
        if sex:
            filters['sex'] = sex
        
        records = self.database.select_records("students", **filters)
        self._print_records(records)
    
    def update_student(self):
        print("\nОбновление записи")
        student_id = self._read_int("Введите id для обновления: ")
        
        existing = self.database.select_records("students", student_id=student_id)
        if not existing:
            print(f"Студент с ID {student_id} не найден.")
            return
        
        current = existing[0]
        print(f"Текущие данные: {current}")
        
        updates = {}
        
        first_name = input(f"Новое имя ({current['first_name']}): ").strip()
        if first_name:
            updates['first_name'] = first_name
        
        second_name = input(f"Новая фамилия ({current['second_name']}): ").strip()
        if second_name:
            updates['second_name'] = second_name
        
        age_input = input(f"Новый возраст ({current['age']}): ").strip()
        if age_input:
            updates['age'] = int(age_input)
        
        sex = input(f"Новый пол ({current['sex']}): ").strip()
        if sex:
            updates['sex'] = sex
        
        if updates:
            try:
                result = self.database.update_record("students", student_id=student_id, **updates)
                if result:
                    print("Запись обновлена")
                else:
                    print("Ошибка при обновлении")
            except Exception as exc:
                print(f"Ошибка: {exc}")
        else:
            print("Нет изменений")
    
    def delete_student(self):
        student_id = self._read_int("Введите id для удаления: ")
        try:
            result = self.database.delete_record("students", student_id)
            if result:
                print(f"Студент с ID {student_id} удален")
            else:
                print(f"Студент с ID {student_id} не найден")
        except Exception as exc:
            print(f"Ошибка: {exc}")
    
    def sort_students(self):
        print("\n=== Сортировка записей ===")
        print("1. По ID\n2. По имени\n3. По фамилии\n4. По возрасту\n5. По полу")
        
        field_choice = input("Выберите поле (1-5): ").strip()
        field_map = {
            "1": "student_id",
            "2": "first_name",
            "3": "second_name",
            "4": "age",
            "5": "sex"
        }
        
        if field_choice not in field_map:
            print("Ошибка: неверный выбор.")
            return
        
        print("1. По возрастанию\n2. По убыванию")
        order_choice = input("Выберите порядок (1-2): ").strip()
        
        if order_choice not in ["1", "2"]:
            print("Ошибка: неверный выбор.")
            return
        
        reverse = (order_choice == "2")
        
        records = self.database.select_records("students")
        if not records:
            print("Нет записей для сортировки")
            return
        
        field = field_map[field_choice]
        sorted_records = sorted(records, key=lambda x: x.get(field), reverse=reverse)
        
        order_str = "убыванию" if reverse else "возрастанию"
        print(f"\n=== Отсортировано по {field} ({order_str}) ===")
        self._print_records(sorted_records)
    
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
            elif action == "0":
                print("Выход из программы.")
                self.running = False
            else:
                print("Неверный выбор. Попробуйте снова.")


def run():
    app = StudentTUI()
    app.run()


if __name__ == "__main__":
    run()