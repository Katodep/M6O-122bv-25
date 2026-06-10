### Класс Table (src/db/backend/table.py)
- Управление структурой таблицы
- Валидация полей при вставке
- Фильтрация и сортировка записей

### Класс StudentTable (src/db/backend/memory.py)
- `create_record()` - добавление записи с валидацией
- `select_record()` - чтение с фильтрацией по полям
- `update_record()` - обновление записи
- `delete_record()` - удаление записи по ID
- `sort_records()` - сортировка записей

### Файловые базы данных (JSON/CSV)
- `create_table()` - создание таблицы
- `insert_record()` - вставка записи
- `select_records()` - выборка с фильтрацией
- `update_record()` - обновление записи
- `delete_record()` - удаление записи

### Класс StudentTUI (src/db/tui.py)
- Выбор типа базы данных при запуске
- Текстовое меню с операциями
- Обработка ошибок ввода

### Сортировка записей
- Поддерживаемые поля: student_id, first_name, second_name, age, sex
- Порядок сортировки: возрастание / убывание

### Обработка ошибок
- `InvalidAgeError` - отрицательный возраст
- `DuplicateIDError` - дублирование ID
- `KeyError` - запись не найдена
- `TableNotFoundError` - таблица не существует
- `InvalidStorageDataError` - повреждение файла

## Тестирование
- Покрытие кода backend: **88%**
- Фреймворк: unittest + pytest

### Запуск тестов
```bash
pytest tests/ --cov=src.db.backend --cov-report=term-missing

![](1698744401294477947.png)