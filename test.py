from src.laguchori_latex.parser import LatexParser
from src.laguchori_latex.generator import LatexGenerator
import os
import json

# Test avec un fichier LaTeX
sample_tex_path = 'sample.tex'
sample_tex_content = r"""
\documentclass{article}
\begin{document}
\section{Introduction}
Ceci est une introduction.
\begin{itemize}
\item Premier point
\item Second point
\end{itemize}
\section{Conclusion}
Ceci est la conclusion.
\end{document}
"""

# Crée un fichier temporaire pour le test
with open(sample_tex_path, 'w', encoding='utf-8') as f:
    f.write(sample_tex_content)

parser = LatexParser()

# Test sur le fichier
result_file = parser.parse_file(sample_tex_path)
print('Résultat du fichier:')
print(result_file)

# Test sur le texte
result_text = parser.parse_text(sample_tex_content)
print('\nRésultat du texte:')
print(result_text)

# Test de génération LaTeX à partir du JSON obtenu
generator = LatexGenerator(preamble_path='preambule.tex')
latex_from_file = generator.json_data_to_latex(result_file)
print('\nLaTeX généré à partir du JSON (fichier):')
print(latex_from_file)

latex_from_text = generator.json_data_to_latex(result_text)
print('\nLaTeX généré à partir du JSON (texte):')
print(latex_from_text)

# Nettoyage du fichier temporaire
os.remove(sample_tex_path)

