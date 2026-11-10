"""Бизнес-логика примитивной базы данных"""

from prettytable import PrettyTable

from .constants import ID_COLUMN, ID_TYPE, VALID_TYPES
from .decorators import confirm_action, handle_db_errors, log_time


def _get_table(metadata, table_name):
    """Возвращает схему таблицы и выбрасывает KeyError, если таблицы нет"""
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')
    return metadata[table_name]


def _check_type(value, expected):
    """Проверка, что значение соответствует ожидаемому типу схемы"""
    if expected == "int":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "bool":
        return isinstance(value, bool)
    if expected == "str":
        return isinstance(value, str)
    return False


def _validate_condition(schema, condition):
    """Проверка, что условие соответствует схеме таблицы."""
    col_types = dict(schema)
    for col, val in condition.items():
        if col not in col_types:
            raise KeyError(f'Столбец "{col}" не существует.')
        if not _check_type(val, col_types[col]):
            raise ValueError(
                f'Некорректное значение для столбца "{col}": {val!r}.'
            )


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Создает новую таблицу в метаданных"""
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')
    for _, col_type in columns:
        if col_type not in VALID_TYPES:
            raise ValueError(f"Некорректное значение: {col_type}.")
    metadata[table_name] = [[ID_COLUMN, ID_TYPE], *columns]
    cols_repr = ", ".join(f"{name}:{typ}" for name, typ in metadata[table_name])
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_repr}')
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удалить таблицу из метаданных"""
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')
    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


@handle_db_errors
def list_tables(metadata):
    """Напечатать список всех таблиц"""
    if not metadata:
        print("Таблиц нет.")
        return
    for name in metadata:
        print(f"- {name}")


@handle_db_errors
@log_time
def insert(metadata, table_name, values, table_data):
    """Добавить новую запись в таблицу"""
    schema = _get_table(metadata, table_name)
    columns = schema[1:]  # исключаем столбец ID
    if len(values) != len(columns):
        raise ValueError(
            f"Ожидалось {len(columns)} значений, получено {len(values)}."
        )
    for (col_name, col_type), value in zip(columns, values):
        if not _check_type(value, col_type):
            raise ValueError(
                f'Некорректное значение для столбца "{col_name}": {value!r}.'
            )
    new_id = max((row[ID_COLUMN] for row in table_data), default=0) + 1
    row = {ID_COLUMN: new_id}
    for (col_name, _), value in zip(columns, values):
        row[col_name] = value
    table_data.append(row)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


@handle_db_errors
@log_time
def select(metadata, table_name, table_data, where_clause=None):
    """Выбрать записи из таблицы и напечатать их через PrettyTable"""
    schema = _get_table(metadata, table_name)
    if where_clause:
        _validate_condition(schema, where_clause)
        rows = [
            row for row in table_data
            if all(row.get(k) == v for k, v in where_clause.items())
        ]
    else:
        rows = list(table_data)
    table = PrettyTable()
    table.field_names = [col for col, _ in schema]
    for row in rows:
        table.add_row([row.get(col) for col, _ in schema])
    print(table)
    return rows


@handle_db_errors
def update(metadata, table_name, table_data, set_clause, where_clause):
    """Обновить подходящие записи в таблице"""
    schema = _get_table(metadata, table_name)
    _validate_condition(schema, set_clause)
    _validate_condition(schema, where_clause)
    updated_ids = []
    for row in table_data:
        if all(row.get(k) == v for k, v in where_clause.items()):
            row.update(set_clause)
            updated_ids.append(row[ID_COLUMN])
    if not updated_ids:
        print("Записи не найдены.")
    else:
        for record_id in updated_ids:
            print(
                f'Запись с ID={record_id} в таблице "{table_name}" '
                f"успешно обновлена."
            )
    return table_data


@handle_db_errors
@confirm_action("удаление записи")
def delete(metadata, table_name, table_data, where_clause):
    """Удалить подходящие записи из таблицы"""
    schema = _get_table(metadata, table_name)
    _validate_condition(schema, where_clause)
    remaining = []
    deleted_ids = []
    for row in table_data:
        if all(row.get(k) == v for k, v in where_clause.items()):
            deleted_ids.append(row[ID_COLUMN])
        else:
            remaining.append(row)
    if not deleted_ids:
        print("Записи не найдены.")
    else:
        for record_id in deleted_ids:
            print(
                f"Запись с ID={record_id} успешно удалена из таблицы "
                f'"{table_name}".'
            )
    return remaining


@handle_db_errors
def info(metadata, table_name, table_data):
    """Напечатать информацию о таблице"""
    schema = _get_table(metadata, table_name)
    cols_repr = ", ".join(f"{name}:{typ}" for name, typ in schema)
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {cols_repr}")
    print(f"Количество записей: {len(table_data)}")