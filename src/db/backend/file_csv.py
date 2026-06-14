import csv
from pathlib import Path
from typing import Any

from .database import Database
from .errors import TableNotFoundError, InvalidStorageDataError
from .table import Table


class CSVDatabase(Database):
    def __init__(self, directory: str = "data_csv") -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.csv"

    def _table_exists(self, table_name: str) -> bool:
        return self._get_table_path(table_name).exists()

    def create_table(self, table_name: str, columns: tuple[str, ...]) -> None:
        table_path = self._get_table_path(table_name)
        if table_path.exists():
            return
        with table_path.open("w", encoding="utf-8", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()

    def _load_table(self, table_name: str) -> Table:
        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")
        try:
            records = []
            with table_path.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                columns = tuple(reader.fieldnames) if reader.fieldnames else ()
                for row in reader:
                    converted_row = {}
                    for key, value in row.items():
                        if key == "student_id" or key == "age":
                            try:
                                converted_row[key] = int(value)
                            except ValueError:
                                converted_row[key] = value
                        else:
                            converted_row[key] = value
                    records.append(converted_row)
        except Exception as e:
            raise InvalidStorageDataError("Файл таблицы содержит некорректные данные.") from e
        return Table(columns, records)

    def _save_table(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)
        with table_path.open("w", encoding="utf-8", newline='') as f:
            if table.records:
                writer = csv.DictWriter(f, fieldnames=table.columns)
                writer.writeheader()
                writer.writerows(table.records)
            else:
                f.write(",".join(table.columns) + "\n")

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