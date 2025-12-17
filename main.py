from typing import Any, Callable

from omd2tex.tools.globals import Global


def time(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that measures and prints execution time.

    Wraps the provided callable, measuring wall-clock duration and printing the elapsed seconds to stdout without altering the wrapped function's behavior.

    Args:
        func: Arbitrary callable to measure; positional and keyword arguments are forwarded unchanged.

    Returns:
        Callable that proxies the original callable and prints the elapsed time before returning the original result.

    Raises:
        Any exception raised by the wrapped callable is propagated unchanged.

    Side Effects:
        Prints timing information to stdout.
    """
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Execute the wrapped callable and print its duration."""
        import time

        start = time.time()

        r = func(*args, **kwargs)
        end = time.time()
        print(f"Time used: {(end - start):.2f} seconds")
        return r

    return wrapper


@time
def main() -> None:
    """Run the demo conversion pipeline using current settings.

    Locates the current markdown filename, adjusts export/search settings, constructs a document, parses it, performs validation, and renders a LaTeX project. Paths and filenames are hardcoded for demonstration and should be adapted for real workflows.

    Args:
        None

    Returns:
        None

    Raises:
        FileNotFoundError: If the current file marker cannot be opened.
        ValueError: Propagated from document processing if initialization fails.

    Side Effects:
        Reads configuration from disk, prints validation output, and writes LaTeX project files to the export directory.

    Examples:
        >>> if __name__ == "__main__":
        ...     main()
    """
    from omd2tex.objects.document import Document
    from omd2tex.tools.settings import Settings

    with open("omd2tex/default/current", "r") as f:
        filename = f.read().strip()

    Settings.Export.search_dir = "~/vzlet_vault/"
    Settings.Export.export_dir = "~/vzlet_vault/LaTeX/"
    Settings.Paragraph.latinify = False
    Settings.Headline.clean_markdown_numeration = True

    filename = "2025-10-05.md"
    filename = "Методичка.md"

    doc = Document()
    doc.from_file(filename)
    doc.check()

    # Settings.Export.check()

    # doc.check()
    # Global.check()
    doc.to_latex_project()


if __name__ == "__main__":
    main()
