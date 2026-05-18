from .backend.memory import StudentTable
from .backend.errors import InvalidAgeError, DuplicateIDError


class StudentTUI:
    def __init__(self):
        self.table = StudentTable()
        self.running = True
    
    def print_menu(self) -> None:
        print("\n=== База студентов ===")
        print("1. Добавить запись")
        print("2. Показать все записи")
        print("3. Найти записи по фильтру")
        print("4. Обновить запись")
        print("5. Удалить по id")
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
    
    def _print_records(self, records: list) -> None:
        if not records:
            print("Записи не найдены.")
            return
        for record in records:
            print(record)
    
    def add_student(self) -> None:
        print("\nДобавление записи")
        student_id = self._read_int("id: ")
        first_name = input("first_name: ").strip()
        second_name = input("second_name: ").strip()
        age = self._read_int("age: ")
        sex = input("sex: ").strip()
        
        try:
            record = self.table.create_record(student_id, first_name, second_name, age, sex)
            print(f"Запись добавлена: {record}")
        except (InvalidAgeError, DuplicateIDError) as exc:
            print(f"Ошибка: {exc}")
    
    def show_all_students(self) -> None:
        print("\nСписок записей")
        self._print_records(self.table.select_record())
    
    def find_students_by_filter(self) -> None:
        print("\nПоиск по фильтру (Enter = пропустить поле)")
        student_id = self._read_optional_int("id: ")
        first_name = input("first_name: ").strip() or None
        second_name = input("second_name: ").strip() or None
        age = self._read_optional_int("age: ")
        sex = input("sex: ").strip() or None
        
        records = self.table.select_record(
            student_id=student_id,
            first_name=first_name,
            second_name=second_name,
            age=age,
            sex=sex,
        )
        self._print_records(records)
    
    def update_student(self) -> None:
        print("\nОбновление записи")
        student_id = self._read_int("Введите id для обновления: ")
        
        try:
            existing = self.table.select_record(student_id=student_id)
            if not existing:
                print(f"Запись с id={student_id} не найдена.")
                return
            
            current = existing[0]
            print(f"Текущие данные: {current}")
            
            first_name = input(f"Новое имя ({current[1]}): ").strip()
            if not first_name:
                first_name = current[1]
            
            second_name = input(f"Новая фамилия ({current[2]}): ").strip()
            if not second_name:
                second_name = current[2]
            
            age_input = input(f"Новый возраст ({current[3]}): ").strip()
            if age_input:
                age = int(age_input)
            else:
                age = current[3]
            
            sex = input(f"Новый пол ({current[4]}): ").strip()
            if not sex:
                sex = current[4]
            
            record = self.table.update_record(student_id, first_name, second_name, age, sex)
            print(f"Запись обновлена: {record}")
        except (ValueError, InvalidAgeError, KeyError) as exc:
            print(f"Ошибка: {exc}")
    
    def delete_student(self) -> None:
        student_id = self._read_int("Введите id для удаления: ")
        try:
            deleted = self.table.delete_record(student_id)
            print(f"Удалена запись: {deleted}")
        except KeyError as exc:
            print(f"Ошибка: {exc}")
    
    def run(self) -> None:
        while self.running:
            self.print_menu()
            action = input("Выберите действие: ").strip()
            
            if action == "1":
                self.add_student()
            elif action == "2":
                self.show_all_students()
            elif action == "3":
                self.find_students_by_filter()
            elif action == "4":
                self.update_student()
            elif action == "5":
                self.delete_student()
            elif action == "0":
                print("Выход из программы.")
                self.running = False
            else:
                print("Неизвестная команда. Повторите ввод.")


def run():
    app = StudentTUI()
    app.run()