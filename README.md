# omd2tex

Markdown to LaTeX converter specified for use with Obsidian.

Requires Python 3.11 or newer.

## Installation

```bash
pip install omd2tex
```

## Usage

```python
from omd2tex.objects.document import Document

document = Document().from_file("note.md")
document.to_latex_project()
```

Configure the input vault and output directory through `Settings.Export.search_dir`
and `Settings.Export.export_dir` before conversion. Included files must stay inside
`search_dir`; exported projects are written below `export_dir`.

## References

- [Beamer theme list](https://github.com/martinbjeldbak/ultimate-beamer-theme-list?tab=readme-ov-file)

## License

This project is licensed under the MIT License.
