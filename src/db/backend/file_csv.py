import csv
from pathlib import Path
from typing import Any

from .database import Database
from .errors import InvalidStorageDataError, TableNotFoundError
from .table import Table


class CSVDatabase(Database):
    def __init__(self, directory: str = "data_csv") -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _table_exists(self, table_name: str) -> bool:
        return self._get_table_path(table_name).exists()

    def _load_table(self, table_name: str) -> Table:
        table_path = self._get_table_path(table_name)
        if not table_path.exists():
            raise TableNotFoundError(f"Таблица '{table_name}' не существует.")

        try:
            with table_path.open("r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                columns = tuple(reader.fieldnames) if reader.fieldnames else ()
                records = []
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
        except Exception as error:
            raise InvalidStorageDataError("Файл таблицы содержит некорректные данные.") from error

        return Table(columns, records)

    def _save_table(self, table_name: str, table: Table) -> None:
        table_path = self._get_table_path(table_name)
        with table_path.open("w", encoding="utf-8", newline='') as file:
            if table.records:
                writer = csv.DictWriter(file, fieldnames=table.columns)
                writer.writeheader()
                writer.writerows(table.records)
            else:
                file.write(",".join(table.columns) + "\n")

    def _get_table_path(self, table_name: str) -> Path:
        return self.directory / f"{table_name}.csv"

    def update_record(self, table_name: str, **updates: Any) -> bool:
        """Обновляет запись в CSV таблице."""
        table = self._load_table(table_name)
        result = table.update_record(**updates)
        if result:
            self._save_table(table_name, table)
        return result

    def delete_record(self, table_name: str, student_id: int) -> bool:
        """Удаляет запись из CSV таблицы."""
        table = self._load_table(table_name)
        result = table.delete_record(student_id)
        if result:
            self._save_table(table_name, table)
        return result