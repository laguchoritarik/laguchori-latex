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

Development 🛠️
License 📄

MIT