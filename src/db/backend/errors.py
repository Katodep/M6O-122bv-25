# src/db/backend/errors.py

class InvalidAgeError(Exception):
    pass

class DuplicateIDError(Exception):
    pass

class MissingColumnError(Exception):
    pass

class UnknownColumnError(Exception):
    pass

class TableAlreadyExistsError(Exception):
    pass

class TableNotFoundError(Exception):
    pass

class InvalidStorageDataError(Exception):
    pass