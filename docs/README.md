# Documentation

Build the HTML docs locally.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r docs/requirements.txt
```

## Build HTML

```bash
cd docs
sphinx-build -b html source _build/html
```

Output appears in `docs/_build/html`. Open `index.html` in a browser to view.

## GitHub Pages

GitHub Pages can publish the docs via GitHub Actions (Source: GitHub Actions). After pushing to `main`, enable Pages in Repository Settings → Pages with Source set to GitHub Actions.

The site uses the PyData Sphinx Theme (pulled in via `docs/requirements.txt`).
