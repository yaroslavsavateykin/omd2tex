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

GitHub Pages can publish the docs via GitHub Actions (Source: GitHub Actions). After pushing to `main`, enable Pages in Repository Settings -> Pages with Source set to GitHub Actions.

The site uses the PyData Sphinx Theme (pulled in via the `docs` extra).

To serve from the `gh-pages` branch (recommended for this workflow):
Settings -> Pages -> Build and deployment -> Source: Deploy from a branch -> Branch: `gh-pages` / folder: `/ (root)`.
