"""Вспомогательные функции для работы с файлами метаданных и данных"""

import json
import os

from .constants import DATA_DIR, META_FILE


def _table_path(table_name: str) -> str:
    """Возвращает путь к json с данными указанной таблицы"""
    return os.path.join(DATA_DIR, f"{table_name}.json")


def delete_table_file(table_name: str) -> None:
    """Удаляет json с данными таблицы, если он существует"""
    path = _table_path(table_name)
    if os.path.exists(path):
        os.remove(path)


def load_metadata(filepath: str = META_FILE) -> dict:
    """Загружает метаданные из json, а при отсутствии файла пустой словарь"""
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath: str, data: dict) -> None:
    """Сохраняет словарь метаданных в json"""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_table_data(table_name: str) -> list:
    """Загружает записи таблицы из json и при отсутствии файла пустой список."""
    try:
        with open(_table_path(table_name), encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: list) -> None:
    """Сохраняет записи таблицы в jsonы"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(_table_path(table_name), "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)