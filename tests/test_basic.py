from laguchori_latex import LatexParser, LatexGenerator

SAMPLE = r"""
\begin{document}
\section{Intro}
Hello
\begin{theorem}
This is a theorem.
\end{theorem}
\end{document}
"""

def test_roundtrip():
    p = LatexParser()
    data = p.parse_text(SAMPLE)

    g = LatexGenerator(preamble_path="does_not_exist.tex")
    latex = g.json_data_to_latex(data)

    assert r"\section{Intro}" in latex
    assert r"\begin{theorem}" in latex
    assert "This is a theorem." in latex
