# laguchori-latex

`laguchori-latex` is a Python library that converts:

- **LaTeX → JSON** (parsing)
- **JSON → LaTeX** (generation)

It is designed to structure a LaTeX document into **sections** and **blocks** (LaTeX environments or free “other” text), then rebuild a `.tex` file from the JSON.

---

## Installation

From PyPI:

```bash
pip install laguchori-latex

From github
pip install "git+https://github.com/laguchoritarik/laguchori-latex.git"

Core idea
JSON structure produced by the parser

The parser outputs a simple structure:

Blocks

env = "other": LaTeX content outside any \begin...\end... environment.

env = "theorem", definition, etc.: content captured from a LaTeX environment.

LaTeX preamble (preambule.tex)

The generator can prepend a preamble at the beginning of the generated .tex.
By default it looks for preambule.tex, but you can change it via preamble_path.

Example preambule.tex

Create a preambule.tex next to your scripts:

\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb,amsthm}
\begin{document}


Important: include \begin{document} in your preamble if you want the output to be directly compilable.

Usage (Python)
1) Parse a LaTeX file → JSON

from laguchori_latex import LatexParser

parser = LatexParser()
data = parser.parse_file("course.tex")

LatexParser.save_json(data, "extracted_elements.json")
2) Parse LaTeX text → JSON
from laguchori_latex import LatexParser

latex_text = r"""
\begin{document}
\section{Intro}
Hello
\begin{theorem}
A theorem text.
\end{theorem}
\end{document}
"""

parser = LatexParser()
data = parser.parse_text(latex_text)
print(data)

3) Generate LaTeX from a JSON file

from laguchori_latex import LatexGenerator

gen = LatexGenerator(preamble_path="preambule.tex")

latex_code = gen.json_file_to_latex("extracted_elements.json")
LatexGenerator.save_latex(latex_code, "output.tex")


4) Generate LaTeX from an in-memory JSON dict
from laguchori_latex import LatexGenerator

data = {
  "document": {
    "sections": [
      {
        "title": "Section 1",
        "blocks": [
          {"env": "other", "content": "Free text.", "order": 0},
          {"env": "theorem", "content": "Theorem content.", "order": 1}
        ]
      }
    ]
  }
}

gen = LatexGenerator(preamble_path="preambule.tex")
latex_code = gen.json_data_to_latex(data)
print(latex_code)
Usage (CLI)

If the CLI entrypoint is enabled in pyproject.toml, you can use:

1) LaTeX → JSON
laguchori-latex parse course.tex -o extracted_elements.json
2) JSON → LaTeX (with preamble)
laguchori-latex generate extracted_elements.json -o output.tex --preamble preambule.tex
End-to-end example (workflow)

You have course.tex

Extract to JSON:
laguchori-latex parse course.tex -o extracted_elements.json
Generate a compilable .tex with a preamble:
laguchori-latex generate extracted_elements.json -o output.tex --preamble preambule.tex
Notes & current limitations

The parser extracts environments of the form: \begin{ENV} ... \end{ENV}

Environment options like \begin{theorem}[Optional title] are not extracted yet.

This structure is useful for:

indexing / RAG

course segmentation

clean document reconstruction

Development

Install dev dependencies:
pip install -e .[dev]
pytest -q
License

MIT

::contentReference[oaicite:0]{index=0}