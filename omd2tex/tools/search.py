import os
import sys
from typing import List, Optional, Tuple


import os
from .settings import Settings


def find_file(filename: str, search_path: Optional[str] = None) -> Optional[str]:
    """Locate a file by name within a search path honoring ignore rules.

    Performs a recursive walk starting from the configured or provided directory, skipping ignored directories, and returns the first path matching the target filename (case-sensitive first, then case-insensitive).

    Args:
        filename: Target filename; path segments are stripped, and trailing whitespace is trimmed.
        search_path: Optional root directory to search; defaults to `Settings.Export.search_dir`, expanded to user home. Falls back to CWD if None.

    Returns:
        Absolute path to the first matching file, or None if not found.

    Raises:
        FileNotFoundError: If the search directory does not exist.

    Side Effects:
        Prints a not-found message to stdout if no match is located; prints comparison errors if they occur.
    """
    exclude_dirs = Settings.Export.search_ignore_dirs

    if search_path is None:
        search_path = Settings.Export.search_dir

    if "/" in filename:
        filename = filename.split("/")[-1]

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


def find_file_flexible(filename: str, search_path: Optional[str] = None) -> Optional[str]:
    """Search for a file using multiple case variants and Unicode normalization.

    Recursively walks the provided directory (or the current working directory by default) and compares several case and normalization variants of the target to discover matches.

    Args:
        filename: Filename to search for; whitespace is preserved except for trailing and leading characters handled externally.
        search_path: Optional root directory; defaults to the current working directory if None. Path is expanded for user home.

    Returns:
        Absolute path of the first matched file, or None if no match is found.

    Raises:
        FileNotFoundError: If the search directory does not exist.

    Side Effects:
        Prints progress and results to stdout during the search.
    """
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
                    print(f"Найден файл: {full_path}")
                    return full_path
            except:
                pass

    print(f"Файл '{filename}' не найден")
    return None


def list_files_in_directory(search_path: Optional[str] = None) -> None:
    """Print directory tree contents for debugging.

    Walks the provided directory (or CWD) and prints folders and files with indentation reflecting depth to stdout.

    Args:
        search_path: Optional directory to list; expanded for user home. Defaults to CWD when None.

    Returns:
        None

    Side Effects:
        Writes directory listings to stdout.
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


def get_image_dimensions(file_path: str) -> Optional[Tuple[int, int]]:
    """Return width and height of an image file if available.

    Attempts to open the file with Pillow and extract its dimensions; returns None if the file is missing or cannot be opened.

    Args:
        file_path: Absolute or relative path to the image file.

    Returns:
        Tuple of (width, height) in pixels when the file is readable, otherwise None.

    Raises:
        None explicitly; FileNotFoundError is caught and suppressed.
    """
    try:
        with Image.open(file_path) as img:
            return img.width, img.height
    except FileNotFoundError:
        return None
