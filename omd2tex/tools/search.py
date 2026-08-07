import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple


import os
from .settings import Settings
from .path_utils import is_relative_to, resolve_relative_to


def find_file(
    filename: str,
    search_path: Optional[str] = None,
    source_dir: Optional[str] = None,
) -> Optional[str]:
    """Locate a file by name using a multi-strategy resolution order.

    Resolution order:
      1. If *filename* is an absolute path and exists, return it immediately.
      2. If *source_dir* is given, try ``source_dir / filename`` (preserving
         any directory component in *filename*, e.g. ``sub/b.md``).
      3. Walk *search_path* (or ``Settings.Export.search_dir`` / CWD) looking
         for a file whose **basename** matches (case-sensitive first, then
         case-insensitive).

    Args:
        filename: Target filename — may include path segments.
        search_path: Root directory for recursive walk.  Defaults to
            ``Settings.Export.search_dir``, expanded for ``~``.
        source_dir: Optional directory of the *referring* document.  When
            given, relative paths are tried against this directory first.

    Returns:
        Absolute path to the first matching file, or ``None``.

    Raises:
        FileNotFoundError: If the resolved search directory does not exist.
    """
    exclude_dirs = Settings.Export.search_ignore_dirs

    if search_path is None:
        search_path = Settings.Export.search_dir

    if search_path is None:
        search_path = os.getcwd()
    else:
        search_path = os.path.expanduser(search_path)

    search_root = Path(search_path).resolve()
    if not search_root.is_dir():
        raise FileNotFoundError(f"Search directory does not exist: {search_path}")

    # Absolute paths are supported only inside the configured vault.
    if os.path.isabs(filename):
        candidate = Path(filename).resolve()
        if candidate.is_file() and is_relative_to(candidate, search_root):
            return str(candidate)
        return None

    # --- Strategy 2: relative to source_dir --------------------------------
    if source_dir is not None:
        source_path = Path(source_dir)
        candidate = resolve_relative_to(filename, source_path)
        if candidate is not None and is_relative_to(candidate, search_root):
            return str(candidate)

    # --- Strategy 3: recursive walk ----------------------------------------
    # Strip path segments for walk-based search (basename only)
    if "/" in filename:
        basename = filename.rsplit("/", 1)[-1]
    else:
        basename = filename

    target_filename = basename.strip()
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
                print(f"Error comparing file {f}: {e}")
                continue

    # --- Diagnostic message -------------------------------------------------
    parts = [f"File '{filename}' not found."]
    if source_dir:
        parts.append(f"  tried relative to source dir: {source_dir}")
    parts.append(f"  tried recursive walk in: {search_path}")
    print(" ".join(parts))
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
