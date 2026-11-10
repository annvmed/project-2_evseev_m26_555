"""Декораторы проекта"""

import functools
import time


def handle_db_errors(func):
    """Перехватывает и сообщает об ошибках, связанных с бд"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as exc:
            message = exc.args[0] if exc.args else str(exc)
            print(f"Ошибка: {message}")
        except ValueError as exc:
            print(f"Ошибка: {exc}")
        except Exception as exc:  # noqa: BLE001
            print(f"Ошибка: {exc}")

    return wrapper


def confirm_action(action_name):
    """Запрашивает у пользователя подтверждение опасного действия"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            ).strip().lower()
            if answer != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Замеряет и выводит время выполнения функции"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start
        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")
        return result

    return wrapper


def create_cacher():
    """Создает функцию кэширования на основе замыкания"""
    cache = {}

    def cache_result(key, value_func):
        """Вернуть значение из кэша по ключу или вычислить и закэшировать"""
        if key in cache:
            return cache[key]
        result = value_func()
        cache[key] = result
        return result

    return cache_result