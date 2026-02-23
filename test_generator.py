from src.laguchori_latex.generator import LatexGenerator
import os

# Exemple de données JSON simulant la sortie du parser
sample_json = {
    "document": {
        "sections": [
            {
                "title": "Introduction",
                "content": "Ceci est une introduction.\\n\\begin{itemize}\\n\\item Premier point\\n\\item Second point\\n\\end{itemize}",
                "blocks": [
                    {"env": "other", "content": "Ceci est une introduction.", "order": 0},
                    {"env": "itemize", "content": "\\n\\item Premier point\\n\\item Second point\\n", "order": 1}
                ]
            },
            {
                "title": "Conclusion",
                "content": "Ceci est la conclusion.",
                "blocks": [
                    {"env": "other", "content": "Ceci est la conclusion.", "order": 0}
                ]
            }
        ]
    }
}

# Sauvegarde un fichier JSON temporaire pour le test
sample_json_path = 'sample.json'
with open(sample_json_path, 'w', encoding='utf-8') as f:
    import json
    json.dump(sample_json, f, ensure_ascii=False, indent=2)

# Test de génération à partir d'un fichier JSON
latex_gen = LatexGenerator(preamble_path='preambule.tex')
latex_code_file = latex_gen.json_file_to_latex(sample_json_path)
print('LaTeX généré depuis un fichier JSON:')
print(latex_code_file)

# Test de génération à partir d'une chaîne JSON
import json
latex_code_text = latex_gen.json_text_to_latex(json.dumps(sample_json))
print('\nLaTeX généré depuis une chaîne JSON:')
print(latex_code_text)

# Nettoyage du fichier temporaire
os.remove(sample_json_path)
