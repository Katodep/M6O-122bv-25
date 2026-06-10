from typing import Any
from .table import Table
from .errors import InvalidAgeError, DuplicateIDError


class StudentTable:
    def __init__(self) -> None:
        self.columns = ("student_id", "first_name", "second_name", "age", "sex")
        self.table = Table(columns=self.columns)
    
    def _get_next_id(self) -> int:
        records = self.table.get_all()
        if not records:
            return 1
        return max(record.get("student_id", 0) for record in records) + 1
    
    def _validate_age(self, age: int) -> None:
        if age < 0:
            raise InvalidAgeError("Поле age не может быть отрицательным.")
    
    def _check_duplicate_id(self, student_id: int) -> None:
        existing = self.table.select_records(student_id=student_id)
        if existing:
            raise DuplicateIDError(f"Запись с id={student_id} уже существует.")
    
    def create_record(
        self,
        student_id: int | None = None,
        first_name: str = "",
        second_name: str = "",
        age: int = 0,
        sex: str = "",
        **kwargs
    ) -> dict[str, Any]:
        if student_id is None or student_id == 0:
            student_id = self._get_next_id()
        
        self._validate_age(age)
        self._check_duplicate_id(student_id)
        
        record = {
            "student_id": student_id,
            "first_name": first_name.strip(),
            "second_name": second_name.strip(),
            "age": age,
            "sex": sex.strip()
        }
        
        self.table.insert_record(record)
        return record.copy()
    
    def select_record(
        self,
        student_id: int | None = None,
        first_name: str | None = None,
        second_name: str | None = None,
        age: int | None = None,
        sex: str | None = None,
        **filters
    ) -> list[dict[str, Any]]:
        if student_id is not None:
            filters["student_id"] = student_id
        if first_name is not None:
            filters["first_name"] = first_name
        if second_name is not None:
            filters["second_name"] = second_name
        if age is not None:
            filters["age"] = age
        if sex is not None:
            filters["sex"] = sex
        
        return self.table.select_records(**filters)
    
    def update_record(
        self,
        student_id: int,
        first_name: str | None = None,
        second_name: str | None = None,
        age: int | None = None,
        sex: str | None = None,
        **kwargs
    ) -> dict[str, Any]:
        existing = self.select_record(student_id=student_id)
        if not existing:
            raise KeyError(f"Запись с id={student_id} не найдена.")
        
        updates = {"student_id": student_id}
        
        if first_name is not None:
            updates["first_name"] = first_name.strip()
        if second_name is not None:
            updates["second_name"] = second_name.strip()
        if age is not None:
            if age < 0:
                raise InvalidAgeError("Поле age не может быть отрицательным.")
            updates["age"] = age
        if sex is not None:
            updates["sex"] = sex.strip()
        
        success = self.table.update_record(**updates)
        if not success:
            raise KeyError(f"Запись с id={student_id} не найдена.")
        
        result = self.select_record(student_id=student_id)
        return result[0] if result else {}
    
    def delete_record(self, student_id: int) -> dict[str, Any]:
        existing = self.select_record(student_id=student_id)
        if not existing:
            raise KeyError(f"Запись с id={student_id} не найдена.")
        
        deleted = existing[0].copy()
        success = self.table.delete_record(student_id)
        
        if not success:
            raise KeyError(f"Запись с id={student_id} не найдена.")
        
        return deleted
    
    def sort_records(self, field: str, reverse: bool = False) -> list[dict[str, Any]]:
        return self.table.sort_records(field, reverse)
    
    def get_all(self) -> list[dict[str, Any]]:
        return self.table.get_all()
    
    # Совместимость с Database интерфейсом для TUI
    def create_table(self, table_name: str, columns: tuple[str, ...]) -> None:
        pass
    
    def insert_record(self, table_name: str, record: dict) -> None:
        self.create_record(**record)
    
    def select_records(self, table_name: str, **filters) -> list:
        return self.select_record(**filters)
    
    def update_record_db(self, table_name: str, **updates) -> bool:
        try:
            student_id = updates.get("student_id")
            if student_id is None:
                return False
            updates_without_id = {k: v for k, v in updates.items() if k != "student_id"}
            self.update_record(student_id=student_id, **updates_without_id)
            return True
        except Exception:
            return False
    
    def delete_record_db(self, table_name: str, student_id: int) -> bool:
        try:
            self.delete_record(student_id)
            return True
        except Exception:
            return False