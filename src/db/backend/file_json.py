import json
from pathlib import Path
from typing import Any

from .database import Database
from .errors import TableNotFoundError
from .table import Table


class JSONDatabase(Database):
    def __init__(self, directory: str = "data") -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
    
    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.json"
    
    def create_table(self, table_name: str, columns: tuple[str, ...]) -> None:
        table_path = self._get_table_path(table_name)
        if table_path.exists():
            return
        table = Table(columns)
        with table_path.open("w", encoding="utf-8") as f:
            json.dump({"columns": list(columns), "records": []}, f, ensure_ascii=False, indent=2)
    
    def _load_table(self, table_name: str) -> Table:
        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")
        
        with table_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        
        return Table(tuple(data["columns"]), data.get("records", []))
    
    def _save_table(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)
        with table_path.open("w", encoding="utf-8") as f:
            json.dump({"columns": list(table.columns), "records": table.records}, f, ensure_ascii=False, indent=2)
    
    def insert_record(self, table_name: str, record: dict[str, Any]) -> None:
        table = self._load_table(table_name)
        table.insert_record(record)
        self._save_table(table_name, table)
    
    def select_records(self, table_name: str, **filters: Any) -> list[dict[str, Any]]:
        table = self._load_table(table_name)
        return table.select_records(**filters)
    
    def update_record(self, table_name: str, **updates: Any) -> bool:
        table = self._load_table(table_name)
        result = table.update_record(**updates)
        if result:
            self._save_table(table_name, table)
        return result
    
    def delete_record(self, table_name: str, student_id: int) -> bool:
        table = self._load_table(table_name)
        result = table.delete_record(student_id)
        if result:
            self._save_table(table_name, table)
        return result