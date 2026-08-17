# Uni-Agent Documentation

This directory contains the source files for the **Uni-Agent** documentation, built with [Sphinx](https://www.sphinx-doc.org/). The docs support both reStructuredText (`.rst`) and Markdown (`.md`).

## Install Dependencies

Install the documentation dependencies before building:

```bash
cd docs
pip install -r requirements.txt
```

## Build the Docs

Generate the static HTML site with:

```bash
make html
```

After the build completes, open the generated homepage:

```text
_build/html/index.html
```

You can also serve the built site locally:

```bash
python -m http.server -d _build/html/
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

## Add New Content

- For Markdown content, add a `.md` file under `source/`.
- For reStructuredText content, add a `.rst` file under `source/`.
- Update the `toctree` in `source/index.rst` so the new page appears in the documentation site.