"""Разбор команд и условий для primitive_db"""

import re
import shlex

INSERT_PATTERN = re.compile(
    r"^insert\s+into\s+(\w+)\s+values\s*\((.*)\)\s*$",
    re.IGNORECASE | re.DOTALL,
)


def split_command(user_input):
    """Разбить строку команды на токены (insert обрабатывается особым образом)"""
    stripped = user_input.strip()
    match = INSERT_PATTERN.match(stripped)
    if match:
        return ["insert", "into", match.group(1), "values", match.group(2)]
    return shlex.split(stripped, posix=False)


def parse_value(token):
    """Преобразовать токен в int, bool или str (в кавычках всегда str)"""
    token = token.strip()
    if not token:
        raise ValueError("пустое значение")
    if len(token) >= 2 and token[0] == token[-1] and token[0] in ('"', "'"):
        return token[1:-1]
    low = token.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    try:
        return int(token)
    except ValueError:
        return token


def parse_values_list(values_str):
    """Разбирает список значений через запятую с учётом кавычек"""
    parts = []
    current = []
    in_quote = None
    for char in values_str:
        if in_quote:
            current.append(char)
            if char == in_quote:
                in_quote = None
        elif char in ('"', "'"):
            in_quote = char
            current.append(char)
        elif char == ",":
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if current:
        parts.append("".join(current).strip())
    return [parse_value(part) for part in parts]


def parse_where_clause(tokens):
    """Разбирает токены '<столбец> = <значение>' в словарь WHERE."""
    if len(tokens) != 3 or tokens[1] != "=":
        raise ValueError("некорректное условие WHERE")
    return {tokens[0]: parse_value(tokens[2])}


def parse_set_clause(tokens):
    """Разбирает токены '<столбец> = <значение>' в словарь SET."""
    if len(tokens) != 3 or tokens[1] != "=":
        raise ValueError("некорректное условие SET")
    return {tokens[0]: parse_value(tokens[2])}