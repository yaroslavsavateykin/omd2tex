import os
import sys


import os
from .settings import Settings


def find_file(filename, search_path=None):
    exclude_dirs = Settings.Export.search_ignore_dirs

    if search_path is None:
        search_path = os.getcwd()
    else:
        search_path = os.path.expanduser(search_path)

    if not os.path.exists(search_path):
        raise FileNotFoundError(f"Directory doesn't exist: {search_path}")

    target_filename = filename.strip()
    target_filename_lower = target_filename.lower()

    if exclude_dirs is None:
        exclude_dirs = []

    exclude_dirs_lower = [d.lower().strip() for d in exclude_dirs if d]

    for root, dirs, files in os.walk(search_path):
        current_dir = os.path.basename(root)

        if current_dir.lower() in exclude_dirs_lower:
            dirs[:] = []
            continue

        for excluded_dir in exclude_dirs:
            if excluded_dir and excluded_dir in root:
                dirs[:] = []
                continue

        for f in files:
            try:
                if f == target_filename:
                    full_path = os.path.join(root, f)
                    return full_path

                if f.lower() == target_filename_lower:
                    full_path = os.path.join(root, f)
                    return full_path

            except Exception as e:
                print(f"Ошибка при сравнении файла {f}: {e}")
                continue

    print(f"File '{filename}' not found")
    return None


def find_file_flexible(filename, search_path=None):
    if search_path is None:
        search_path = os.getcwd()
    else:
        search_path = os.path.expanduser(search_path)

    if not os.path.exists(search_path):
        raise FileNotFoundError(f"Directory doesn't exist: {search_path}")

    target_filename = filename.strip()

    print(f"Ищу файл: '{target_filename}' в директории: {search_path}")

    search_variants = [
        target_filename,
        target_filename.lower(),
        target_filename.upper(),
    ]

    for root, dirs, files in os.walk(search_path):
        for f in files:
            file_variants = [
                f,
                f.lower(),
                f.upper(),
            ]

            if target_filename in file_variants or f in search_variants:
                full_path = os.path.join(root, f)
                print(f"Найден файл: {full_path}")
                return full_path

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


def list_files_in_directory(search_path=None):
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
    try:
        with Image.open(file_path) as img:
            return img.width, img.height
    except FileNotFoundError:
        return None
