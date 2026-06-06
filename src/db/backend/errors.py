# src/db/backend/errors.py

class StudentTableError(Exception):
    """Базовый класс для ошибок, связанных с таблицей Student."""
    pass


class InvalidAgeError(StudentTableError):
    """Ошибка при попытке создать запись с некорректным возрастом."""
    pass


class DuplicateIDError(StudentTableError):
    """Ошибка при попытке создать запись с уже существующим ID."""
    pass


class DatabaseError(Exception):
    """Базовый класс для ошибок базы данных."""
    pass


class TableAlreadyExistsError(DatabaseError):
    """Ошибка при попытке создать уже существующую таблицу."""
    pass


class TableNotFoundError(DatabaseError):
    """Ошибка при обращении к несуществующей таблице."""
    pass


class MissingColumnError(DatabaseError):
    """Ошибка при отсутствии обязательного поля в записи."""
    pass


class UnknownColumnError(DatabaseError):
    """Ошибка при использовании поля, которого нет в схеме."""
    pass


class InvalidStorageDataError(DatabaseError):
    """Ошибка при чтении повреждённых данных из файла."""
    pass