# omd2tex

Markdown to LaTeX converter specified for use with Obsidian.

## Install

```bash
uv pip install omd2tex
```

## Development (uv)

```bash
uv venv
uv pip install -e ".[dev,test,docs]"
```

Run tests:

```bash
uv run pytest
```

## Build and publish

```bash
uv pip install build twine
uv run python -m build
uv run twine upload dist/*
```

## Documentation


## References

- [Beamer theme list](https://github.com/martinbjeldbak/ultimate-beamer-theme-list?tab=readme-ov-file)

## License

This project is licensed under the MIT License.
