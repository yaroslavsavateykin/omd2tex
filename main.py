import re
from pathlib import Path
from typing import Any, Callable


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
    from omd2tex.objects.document import Document
    from omd2tex.tools.settings import Settings

    project_dir = Path(__file__).resolve().parent
    translation_dir = project_dir / "Translation"
    export_dir = project_dir / "Scripts"

    Settings.Export.search_dir = str(translation_dir)
    Settings.Export.export_dir = str(export_dir)
    Settings.Image.absolute_path_in_project_export = True
    Settings.Paragraph.latinify = False

    doc = Document()
    doc.from_file("Translation.md")
    doc.to_latex_project()
    cleanup_generated_tex(export_dir / "Translation")


DISPLAY_MATH_BEGIN = re.compile(
    r"^\s*\\begin\{(align\*?|displaymath|equation\*?|gather\*?|multline\*?)\}\s*$"
)
DISPLAY_MATH_END = re.compile(
    r"^\s*\\end\{(align\*?|displaymath|equation\*?|gather\*?|multline\*?)\}\s*$"
)


def cleanup_generated_tex(output_dir: Path) -> None:
    """Remove blank lines inside display-math environments in generated TeX."""
    for tex_file in output_dir.glob("*.tex"):
        lines = tex_file.read_text(encoding="utf-8").splitlines()
        cleaned_lines = []
        in_display_math = False

        for line in lines:
            stripped = line.strip()

            if DISPLAY_MATH_BEGIN.match(stripped):
                in_display_math = True
                cleaned_lines.append(line)
                continue

            if DISPLAY_MATH_END.match(stripped):
                in_display_math = False
                cleaned_lines.append(line)
                continue

            if in_display_math and not stripped:
                continue

            cleaned_lines.append(line)

        tex_file.write_text("\n".join(cleaned_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
