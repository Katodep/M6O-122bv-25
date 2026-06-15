from abc import ABC, abstractmethod
from typing import Any


class Database(ABC):
    @abstractmethod
    def create_table(self, table_name: str, columns: tuple[str, ...]) -> None:
        pass
    
    @abstractmethod
    def insert_record(self, table_name: str, record: dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    def select_records(self, table_name: str, **filters: Any) -> list[dict[str, Any]]:
        pass
    
    @abstractmethod
    def update_record(self, table_name: str, **updates: Any) -> bool:
        pass
    
    @abstractmethod
    def delete_record(self, table_name: str, student_id: int) -> bool:
        pass