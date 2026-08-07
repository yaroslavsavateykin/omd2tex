# Documentation

Build the HTML docs locally with uv.

## Setup

```bash
uv venv
uv pip install -e ".[docs]"
```

## Build HTML

```bash
uv run sphinx-build -b html docs/source docs/_build/html
```

Output appears in `docs/_build/html`. Open `index.html` in a browser to view.

## GitHub Pages

After pushing to `main`, serve the generated site from the workflow's `gh-pages` branch:
Settings -> Pages -> Build and deployment -> Source: Deploy from a branch -> Branch: `gh-pages` / folder: `/ (root)`.

The site uses the PyData Sphinx Theme (pulled in via the `docs` extra).
