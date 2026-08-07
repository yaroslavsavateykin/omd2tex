"""Centralised path helpers for omd2tex.

All path resolution, normalisation and default-dir lookups live here so that
the rest of the project can import small, well-tested functions instead of
re-implementing the same ``os.path`` / string tricks everywhere.
"""

from pathlib import Path
from typing import Optional


def package_default_dir() -> Path:
    """Return the absolute path to the ``omd2tex/default/`` resource directory."""
    return Path(__file__).resolve().parent.parent / "default"


def normalize_export_dir(raw: str) -> str:
    """Expand ``~`` and strip a trailing ``/`` from an export-dir setting.

    Returns a *string* so that callers that still store dirs as ``str`` work
    unchanged.
    """
    return str(Path(raw).expanduser())


def stem_md(filename: str) -> str:
    """Remove the ``.md`` suffix from *filename* if present.

    Unlike ``str.strip(".md")`` (which strips a *character set*), this
    function only removes the literal ``".md"`` suffix.

    >>> stem_md("damage.md")
    'damage'
    >>> stem_md("readme")
    'readme'
    """
    if filename.endswith(".md"):
        return filename[:-3]
    return filename


def export_project_name(filename: str) -> str:
    """Return a safe project-directory name derived from a Markdown filename."""
    name = Path(str(filename).replace("\\", "/")).name
    name = stem_md(name)
    if name in {"", ".", ".."}:
        raise ValueError("Filename must contain a project name")
    return name


def is_relative_to(path: Path, parent: Path) -> bool:
    """Return whether *path* is contained in *parent*, resolving symlinks."""
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def resolve_relative_to(path_str: str, source_dir: Optional[Path]) -> Optional[Path]:
    """Try to resolve *path_str* relative to *source_dir*.

    Returns the resolved ``Path`` if the file exists, otherwise ``None``.
    """
    if source_dir is None:
        return None
    candidate = (source_dir / path_str).resolve()
    if candidate.is_file():
        return candidate
    return None
