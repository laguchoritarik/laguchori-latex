The library transforms raw LaTeX files into a structured JSON format based on logical blocks. This allows LLMs to process mathematical content without being overwhelmed by LaTeX formatting commands.
JSON Structure Produced

The parser outputs a consistent hierarchical structure:

    env = "other": Capture plain text or LaTeX commands located outside any \begin...\end environment.

    env = "theorem", "definition", "equation", etc.: Capture structured content from specific LaTeX environments.

Preamble Configuration 🛠️

The generator can prepend a LaTeX preamble to ensure the output is a stand-alone, compilable document. By default, it looks for a file named preambule.tex.
Example preambule.tex

Create a preambule.tex in your working directory:

    Note: Including \begin{document} in your preamble is required if you want the generated output to be directly compilable.

Usage (Python API) 🐍
1. Parse a LaTeX file to JSON
2. Parse raw LaTeX text directly
3. Generate LaTeX from a JSON file
4. Generate LaTeX from an in-memory JSON dictionary
Command Line Interface (CLI) 💻

If enabled in your pyproject.toml, you can use the library directly from your terminal:

Convert LaTeX to JSON:

Convert JSON to LaTeX:
Notes & Current Limitations ⚠️

    Scope: The parser currently targets standard environments of the form \begin{ENV} ... \end{ENV}.

    Metadata: Environment options (e.g., \begin{theorem}[Optional title]) are currently kept within the content block and not yet extracted as separate metadata.

    Applications: This library is ideal for:

        RAG / AI Search: Indexing mathematical proofs by semantic chunks.

        Educational Platforms: Segmenting long courses into manageable units.

        Automated Publishing: Programmatically generating LaTeX documents from structured data.


What this library does
Parsing (LaTeX → JSON)

Reads LaTeX content (from a file or a string)

Removes some commands that are not needed for structure extraction (e.g., \label, \cite, \ref, \eqref)

Extracts the content between ```latex \begin{document} and \end{document} ```

Splits the document into \section{...}

Extracts LaTeX environments inside each section:
```latex
\begin{theorem}...\end{theorem}

\begin{definition}...\end{definition}
```
etc.

Anything that is not inside an environment is stored as a block with env="other".

Generation (JSON → LaTeX)

Loads JSON (file or JSON string) or accepts a Python dict

Generates LaTeX sections and blocks in the right order

Optionally prepends a LaTeX preamble from preambule.tex

Appends \end{document} at the end

JSON format

The parser returns a structure like:
```json
{
  "document": {
    "sections": [
      {
        "title": "Intro",
        "content": "...",
        "blocks": [
          { "env": "other", "content": "Some text", "order": 0 },
          { "env": "theorem", "content": "Theorem text", "order": 1 }
        ]
      }
    ]
  }
}
```


## Blocks

env = "other": LaTeX text outside any \begin...\end... environment.

env = "theorem", definition, remark, etc.: content captured from that environment.

order: used to preserve the original order of blocks in a section.

LaTeX preamble (preambule.tex)

The generator can prepend a preamble at the beginning of the generated .tex.

Default path: preambule.tex

You can change it via LatexGenerator(preamble_path="...")

Example preambule.tex

Create a file called preambule.tex next to your scripts:
```latex
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb,amsthm}
\begin{document}
```

### Important: include \begin{document} in your preamble if you want the output .tex to be directly compilable.

Python API
LatexParser

### Import:

from laguchori_latex import LatexParser

### Methods

parse_file(path: str) -> dict
Parse a .tex file and return structured JSON (dict).

parse_text(text: str) -> dict
Parse LaTeX content provided as a string.

save_json(data: dict, path: str) -> None (static)
Save JSON dict into a file.

### Example: parse a file
```python
from laguchori_latex import LatexParser

parser = LatexParser()
data = parser.parse_file("course.tex")

LatexParser.save_json(data, "extracted_elements.json")
```

### Example: parse LaTeX text
```python
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
```
## LatexGenerator

### Import:
```python
from laguchori_latex import LatexGenerator
```
Constructor

LatexGenerator(preamble_path: str = "preambule.tex")
Loads a preamble from preamble_path if the file exists.

### Methods

json_file_to_latex(json_path: str) -> str
Load JSON from a file and generate LaTeX.

json_text_to_latex(json_text: str) -> str
Load JSON from a string and generate LaTeX.

json_data_to_latex(data: dict) -> str
Generate LaTeX from an in-memory dict.

save_latex(latex_code: str, path: str) -> None (static)
Save LaTeX code into a .tex file.

## Example: generate .tex from JSON file
```python
from laguchori_latex import LatexGenerator

gen = LatexGenerator(preamble_path="preambule.tex")
latex_code = gen.json_file_to_latex("extracted_elements.json")

LatexGenerator.save_latex(latex_code, "output.tex")
```
Example: generate .tex from Python dict
```python
from laguchori_latex import LatexGenerator
```json
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
```
```python
gen = LatexGenerator(preamble_path="preambule.tex")
latex_code = gen.json_data_to_latex(data)
print(latex_code)
```
## CLI

If you enabled the CLI entrypoint in pyproject.toml, you can use:

### LaTeX → JSON

laguchori-latex parse course.tex -o extracted_elements.json

### JSON → LaTeX (with preamble)

laguchori-latex generate extracted_elements.json -o output.tex --preamble preambule.tex

# End-to-end example
## Step 1 — Parse LaTeX into JSON

laguchori-latex parse course.tex -o extracted_elements.json

 ## Step 2 — Regenerate a compilable .tex

laguchori-latex generate extracted_elements.json -o output.tex --preamble preambule.tex

Limitations

The parser extracts environments of the form:
```latex
\begin{ENV} ... \end{ENV}
```

Environment options like:
```latex
\begin{theorem}[Optional title]
```
are not extracted yet.

Only \section{...} is handled (no \subsection yet).

## Development

Install dev dependencies:
```cli
pip install -e .[dev]
pytest -q
```


## OCR-to-Clean LaTeX Cleaner

`laguchori-latex` includes an optional **OCR-to-clean LaTeX** cleaner designed for math lecture notes that come from OCR/PDF extraction.  
It converts common “scanned course” patterns into structured LaTeX environments and headings, making downstream parsing and chunking much more reliable.

### What it fixes / normalizes

The cleaner targets patterns frequently produced by OCR:

#### 1) Bold numbered titles → LaTeX headings (numbers removed)
- `\textbf{2 Groupe orthogonal}` → `\section{Groupe orthogonal}`
- `\textbf{2.1 Produit scalaire}` → `\subsection{Produit scalaire}`
- `\textbf{2.1.3 Notation}` → `\subsubsection{Notation}`

The numeric prefix is used only to infer the heading level and is **not** kept in the title.

#### 2) Existing LaTeX headings → remove leading numbering (Arabic or Roman)
- `\section{VI Positivité}` → `\section{Positivité}`
- `\section{2 Le groupe $O_2(\mathbb{R})$}` → `\section{Le groupe $O_2(\mathbb{R})$}`

This is implemented with a brace-aware parser, so titles containing nested braces/macros (e.g., `\mathbb{R}`) are handled correctly.

#### 3) Statement headers → structured theorem-like environments
It recognizes statement headers such as:
- `Théorème 8. ...`
- `\textbf{Proposition 16.} ...`
- `Lemme 1. ...`
- `Corollaire 4. ...`
- `\textbf{Définition 16.} ...`
- `\textbf{Exemple 2.} ...`

and converts them into environments:
- `theorem`, `proposition`, `lemma`, `corollary`, `definition`, `example`

The OCR number is **not** reused in the resulting LaTeX output.

#### 4) Proofs / remarks / variants
- `Démonstration. ...` / `\textit{Démonstration.} ...` / `Démonstration 15. ...`
  → `\begin{proof}...\end{proof}`
- `Remarque : ...` / `\textbf{Remarque :} ...` / `Variante. ...`
  → `\begin{remark}...\end{remark}`

#### 5) Pedagogical blocks
- `\textbf{Notations :}` → `\begin{notation}...\end{notation}`
- `\textbf{Exemples :}` → `\begin{examples}...\end{examples}`
- `\textbf{Remarques :}` → `\begin{remark}...\end{remark}` (plural form supported)

### API

#### `clean_text(text: str, *, add_labels: bool = True, strip_numeric_prefix_in_sections: bool = True) -> str`

Cleans OCR-like LaTeX text and returns a cleaned LaTeX string.

- `add_labels` (default `True`): auto-generates `\label{...}` for theorem-like environments.
  - If a statement has a title `( ... )`, the label is based on a slug of that title.
  - Otherwise labels are sequential per environment type: `thm:1`, `thm:2`, `prop:1`, etc.
- `strip_numeric_prefix_in_sections` (default `True`): removes leading Arabic/Roman numbering from `\section{...}`, `\subsection{...}`, etc.

#### `clean_file(input_path: str, output_path: str, *, add_labels: bool = True, strip_numeric_prefix_in_sections: bool = True) -> None`

Reads a `.tex` file, cleans it, and writes the cleaned output to a new file.

### Quick start examples

#### Example 1 — Clean a file before parsing
```python
from laguchori_latex import LatexParser, clean_file

clean_file("input.tex", "output.tex", add_labels=True)

parser = LatexParser()
data = parser.parse_file("output.tex")


### Example 2 — Clean text directly
from laguchori_latex import clean_text

raw = r"\section{2 Le groupe $O_2(\mathbb{R})$}"
print(clean_text(raw))
# -> \section{Le groupe $O_2(\mathbb{R})$}

Example 3 — Use inside parsing (optional)

If you added preclean=True support in LatexParser.parse_file:


Development 🛠️
License 📄

MIT
