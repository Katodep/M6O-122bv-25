from typing import Any
from .database import Database
from .errors import InvalidAgeError, DuplicateIDError, UnknownColumnError


class StudentTable(Database):
    def __init__(self) -> None:
        self._student: list[dict[str, Any]] = []
        self.columns = ("student_id", "first_name", "second_name", "age", "sex")
    
    def _get_next_id(self) -> int:
        if not self._student:
            return 1
        return max(record.get("student_id", 0) for record in self._student) + 1
    
    def _validate_columns(self, record: dict[str, Any]) -> None:
        for key in record:
            if key not in self.columns:
                raise UnknownColumnError(f"Поле '{key}' не определено в структуре таблицы.")
    
    def create_table(self, table_name: str, columns: tuple[str, ...]) -> None:
        self.columns = columns
    
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
        
        if age < 0:
            raise InvalidAgeError("Поле age не может быть отрицательным.")
        
        if any(record.get("student_id") == student_id for record in self._student):
            raise DuplicateIDError(f"Запись с id={student_id} уже существует.")
        
        new_record = {
            "student_id": student_id,
            "first_name": first_name.strip(),
            "second_name": second_name.strip(),
            "age": age,
            "sex": sex.strip()
        }
        self._validate_columns(new_record)
        self._student.append(new_record)
        return new_record.copy()
    
    def select_records(self, table_name: str, **filters: Any) -> list[dict[str, Any]]:
        if not filters:
            return [r.copy() for r in self._student]
        
        result = []
        for record in self._student:
            match = True
            for key, value in filters.items():
                if record.get(key) != value:
                    match = False
                    break
            if match:
                result.append(record.copy())
        return result
    
    def select_record(self, **filters: Any) -> list[dict[str, Any]]:
        return self.select_records("students", **filters)
    
    def insert_record(self, table_name: str, record: dict[str, Any]) -> None:
        self.create_record(**record)
    
    def update_record(self, table_name: str, **updates: Any) -> bool:
        try:
            student_id = updates.get("student_id")
            if student_id is None:
                return False
            
            for i, record in enumerate(self._student):
                if record.get("student_id") == student_id:
                    for key, value in updates.items():
                        if key != "student_id":
                            if key not in self.columns:
                                raise UnknownColumnError(f"Поле '{key}' не определено в структуре таблицы.")
                            if key == "age" and value < 0:
                                return False
                            self._student[i][key] = value
                    return True
            return False
        except (KeyError, TypeError, ValueError):
            return False
    
    def delete_record(self, table_name: str, student_id: int) -> bool:
        try:
            for i, record in enumerate(self._student):
                if record.get("student_id") == student_id:
                    self._student.pop(i)
                    return True
            return False
        except (KeyError, ValueError):
            return False
    
    def sort_records(self, field: str, reverse: bool = False) -> list[dict[str, Any]]:
        if not self._student:
            return []
        if field not in self.columns:
            raise UnknownColumnError(f"Поле '{field}' не определено в структуре таблицы.")
        return sorted(self._student, key=lambda x: x.get(field), reverse=reverse)
    
    def get_all(self) -> list[dict[str, Any]]:
        return [r.copy() for r in self._student]
    
    def _table_exists(self, table_name: str) -> bool:
        return True
    
    def _load_table(self, table_name: str):
        return self
    
    def _save_table(self, table_name: str, table) -> None:
        pass