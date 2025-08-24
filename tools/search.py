import os
import sys


import os
from .settings import Settings


def find_file(filename, search_path=None):
    """
    Ищет файл в текущей директории и её поддиректориях, исключая указанные папки.

    Параметры:
        filename (str): Имя файла для поиска (например "file.txt")
        search_path (str, optional): Стартовая директория. По умолчанию - текущая.
        exclude_dirs (list, optional): Список папок для исключения из поиска.

    Возвращает:
        str: Абсолютный путь к файлу если найден, иначе None.
    """
    exclude_dirs = Settings.Export.search_ignore_dirs

    if search_path is None:
        search_path = os.getcwd()
    else:
        search_path = os.path.expanduser(search_path)

    if not os.path.exists(search_path):
        raise FileNotFoundError(f"Directory doesn't exist: {search_path}")

    # Нормализуем имя файла для поиска
    target_filename = filename.strip()
    target_filename_lower = target_filename.lower()

    # Нормализуем список исключаемых папок
    if exclude_dirs is None:
        exclude_dirs = []

    # Приводим все исключаемые папки к нижнему регистру для сравнения
    exclude_dirs_lower = [d.lower().strip() for d in exclude_dirs if d]

    # print(f"Ищу файл: '{target_filename}' в директории: {search_path}")
    # print(f"Исключаемые папки: {exclude_dirs}")

    for root, dirs, files in os.walk(search_path):
        # Получаем имя текущей директории из пути
        current_dir = os.path.basename(root)

        # Проверяем, не находится ли текущая директория в списке исключений
        if current_dir.lower() in exclude_dirs_lower:
            # print(f"Пропускаем директорию: {root}")
            dirs[:] = []  # Очищаем список поддиректорий для os.walk
            continue

        # Также проверяем полный путь на исключения (на случай, если нужно исключить по полному пути)
        for excluded_dir in exclude_dirs:
            if excluded_dir and excluded_dir in root:
                # print(f"Пропускаем путь: {root} (содержит исключенную папку)")
                dirs[:] = []
                continue

        for f in files:
            try:
                # Прямое сравнение
                if f == target_filename:
                    full_path = os.path.join(root, f)
                    return full_path

                # Сравнение без регистра
                if f.lower() == target_filename_lower:
                    full_path = os.path.join(root, f)
                    return full_path

            except Exception as e:
                print(f"Ошибка при сравнении файла {f}: {e}")
                continue

    print(f"File '{filename}' not found")
    return None


# Альтернативная версия с более гибким поиском
def find_file_flexible(filename, search_path=None):
    """
    Более гибкий поиск файлов с поддержкой различных кодировок
    """
    if search_path is None:
        search_path = os.getcwd()
    else:
        search_path = os.path.expanduser(search_path)

    if not os.path.exists(search_path):
        raise FileNotFoundError(f"Directory doesn't exist: {search_path}")

    target_filename = filename.strip()

    print(f"Ищу файл: '{target_filename}' в директории: {search_path}")

    # Попробуем разные способы нормализации
    search_variants = [
        target_filename,  # оригинальное имя
        target_filename.lower(),  # нижний регистр
        target_filename.upper(),  # верхний регистр
    ]

    for root, dirs, files in os.walk(search_path):
        for f in files:
            # Нормализуем имя найденного файла
            file_variants = [
                f,
                f.lower(),
                f.upper(),
            ]

            # Проверяем все комбинации
            if target_filename in file_variants or f in search_variants:
                full_path = os.path.join(root, f)
                print(f"Найден файл: {full_path}")
                return full_path

            # Проверка с нормализацией Unicode
            try:
                import unicodedata

                normalized_target = unicodedata.normalize("NFC", target_filename)
                normalized_file = unicodedata.normalize("NFC", f)
                if normalized_target == normalized_file:
                    full_path = os.path.join(root, f)
                    print(f"Найден файл (Unicode нормализация): {full_path}")
                    return full_path
            except:
                pass

    print(f"Файл '{filename}' не найден")
    return None


# Для отладки - функция показывает все файлы в директории
def list_files_in_directory(search_path=None):
    """
    Вспомогательная функция для отладки - показывает все файлы в директории
    """
    if search_path is None:
        search_path = os.getcwd()
    else:
        search_path = os.path.expanduser(search_path)

    print(f"Содержимое директории {search_path}:")
    for root, dirs, files in os.walk(search_path):
        level = root.replace(search_path, "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")


def get_image_dimensions(file_path):
    """Получает ширину и высоту изображения."""
    try:
        with Image.open(file_path) as img:
            return img.width, img.height
    except FileNotFoundError:
        return None
