"""Главный цикл и обработка команд primitive_db"""

import prompt

from . import core
from .constants import META_FILE, VALID_TYPES
from .parser import (
    parse_set_clause,
    parse_values_list,
    parse_where_clause,
    split_command,
)
from .utils import (
    delete_table_file,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def welcome():
    """Напечатать приветственное сообщение."""
    print("***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")


def print_help():
    """Напечатать полную справку по командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> <столбец1:тип> "
        "<столбец2:тип> .. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\n***Операции с данными***")
    print("Функции:")
    print(
        "<command> insert into <имя_таблицы> values "
        "(<значение1>, <значение2>, ...) - создать запись."
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = "
        "<значение> - прочитать записи по условию."
    )
    print("<command> select from <имя_таблицы> - прочитать все записи.")
    print(
        "<command> update <имя_таблицы> set <столбец1> = "
        "<новое_значение1> where <столбец_условия> = "
        "<значение_условия> - обновить запись."
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = "
        "<значение> - удалить запись."
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице.")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def _handle_create_table(tokens):
    """Обработать команду create_table."""
    if len(tokens) < 3:
        print("Некорректная команда create_table.")
        return
    table_name = tokens[1]
    columns = []
    for col_def in tokens[2:]:
        if ":" not in col_def:
            print(f"Некорректное значение: {col_def}. Попробуйте снова.")
            return
        col_name, col_type = col_def.split(":", 1)
        if col_type not in VALID_TYPES:
            print(f"Некорректное значение: {col_type}. Попробуйте снова.")
            return
        columns.append((col_name, col_type))
    metadata = load_metadata(META_FILE)
    result = core.create_table(metadata, table_name, columns)
    if result is not None:
        save_metadata(META_FILE, result)


def _handle_drop_table(tokens):
    """Обработать команду drop_table."""
    if len(tokens) != 2:
        print("Некорректная команда drop_table.")
        return
    table_name = tokens[1]
    metadata = load_metadata(META_FILE)
    result = core.drop_table(metadata, table_name)
    if result is not None:
        save_metadata(META_FILE, result)
        delete_table_file(table_name)


def _handle_list_tables():
    """Обработать команду list_tables."""
    metadata = load_metadata(META_FILE)
    core.list_tables(metadata)


def _handle_insert(tokens):
    """Обработать команду insert."""
    if len(tokens) < 5:
        print("Некорректная команда insert.")
        return
    table_name = tokens[2]
    try:
        values = parse_values_list(tokens[4])
    except ValueError:
        print("Некорректное значение. Попробуйте снова.")
        return
    metadata = load_metadata(META_FILE)
    table_data = load_table_data(table_name)
    result = core.insert(metadata, table_name, values, table_data)
    if result is not None:
        save_table_data(table_name, result)


def _handle_select(tokens):
    """Обработать команду select."""
    if len(tokens) < 3 or tokens[1] != "from":
        print("Некорректная команда select.")
        return
    table_name = tokens[2]
    where_clause = None
    if len(tokens) > 3:
        if tokens[3] != "where" or len(tokens) != 7:
            print("Некорректная команда select.")
            return
        try:
            where_clause = parse_where_clause(tokens[4:])
        except ValueError as exc:
            print(f"Некорректное значение. {exc}.")
            return
    metadata = load_metadata(META_FILE)
    table_data = load_table_data(table_name)
    core.select(metadata, table_name, table_data, where_clause)


def _handle_update(tokens):
    """Обработать команду update."""
    if len(tokens) < 6 or tokens[2] != "set":
        print("Некорректная команда update.")
        return
    table_name = tokens[1]
    try:
        where_idx = tokens.index("where", 3)
    except ValueError:
        print("Некорректная команда update: отсутствует where.")
        return
    try:
        set_clause = parse_set_clause(tokens[3:where_idx])
        where_clause = parse_where_clause(tokens[where_idx + 1:])
    except ValueError as exc:
        print(f"Некорректное значение. {exc}.")
        return
    metadata = load_metadata(META_FILE)
    table_data = load_table_data(table_name)
    result = core.update(
        metadata, table_name, table_data, set_clause, where_clause
    )
    if result is not None:
        save_table_data(table_name, result)


def _handle_delete(tokens):
    """Обработать команду delete."""
    if len(tokens) != 7 or tokens[1] != "from" or tokens[3] != "where":
        print("Некорректная команда delete.")
        return
    table_name = tokens[2]
    try:
        where_clause = parse_where_clause(tokens[4:])
    except ValueError as exc:
        print(f"Некорректное значение. {exc}.")
        return
    metadata = load_metadata(META_FILE)
    table_data = load_table_data(table_name)
    result = core.delete(metadata, table_name, table_data, where_clause)
    if result is not None:
        save_table_data(table_name, result)


def _handle_info(tokens):
    """Обработать команду info."""
    if len(tokens) != 2:
        print("Некорректная команда info.")
        return
    table_name = tokens[1]
    metadata = load_metadata(META_FILE)
    table_data = load_table_data(table_name)
    core.info(metadata, table_name, table_data)


def run():
    """Запустить основной цикл приложения."""
    welcome()
    while True:
        try:
            user_input = prompt.string("Введите команду: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_input:
            continue
        tokens = split_command(user_input)
        if not tokens:
            continue
        command = tokens[0].lower()
        if command in ("exit", "quit"):
            break
        if command in ("help", "database"):
            print_help()
        elif command == "create_table":
            _handle_create_table(tokens)
        elif command == "drop_table":
            _handle_drop_table(tokens)
        elif command == "list_tables":
            _handle_list_tables()
        elif command == "insert":
            _handle_insert(tokens)
        elif command == "select":
            _handle_select(tokens)
        elif command == "update":
            _handle_update(tokens)
        elif command == "delete":
            _handle_delete(tokens)
        elif command == "info":
            _handle_info(tokens)
        else:
            print(f"Функции {tokens[0]} нет. Попробуйте снова.")