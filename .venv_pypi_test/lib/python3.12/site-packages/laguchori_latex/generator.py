import json
import os

class LatexGenerator:
	"""
	Génère du code LaTeX à partir d'un fichier JSON ou d'une chaîne JSON.
	"""
	def __init__(self, preamble_path='preambule.tex'):
		self.preamble = self.get_preamble(preamble_path)

	@staticmethod
	def get_preamble(path='preambule.tex'):
		"""Lit le préambule LaTeX depuis un fichier si disponible."""
		if os.path.exists(path):
			with open(path, 'r', encoding='utf-8') as f:
				return f.read()
		return ''

	def json_file_to_latex(self, json_path):
		"""
		Génère du LaTeX à partir d'un fichier JSON.
		Args:
			json_path (str): Chemin du fichier JSON.
		Returns:
			str: Code LaTeX généré.
		"""
		with open(json_path, 'r', encoding='utf-8') as f:
			data = json.load(f)
		return self.json_data_to_latex(data)

	def json_text_to_latex(self, json_text):
		"""
		Génère du LaTeX à partir d'une chaîne JSON.
		Args:
			json_text (str): Chaîne JSON.
		Returns:
			str: Code LaTeX généré.
		"""
		data = json.loads(json_text)
		return self.json_data_to_latex(data)

	def json_data_to_latex(self, data):
		"""
		Génère du LaTeX à partir d'un objet Python (dict) issu du JSON.
		Args:
			data (dict): Données JSON déjà chargées.
		Returns:
			str: Code LaTeX généré.
		"""
		latex = self.preamble
		sections = data['document']['sections']
		for section in sections:
			latex += '\\section{' + section['title'] + '}\n'
			for block in sorted(section['blocks'], key=lambda b: b['order']):
				if block['env'] == 'other':
					latex += block['content'] + '\n'
				else:
					opt = ''
					if 'option' in block and block['option']:
						opt = '[' + block['option'] + ']'
					latex += f"\\begin{{{block['env']}}}{opt}{block['content']}\\end{{{block['env']}}}\n"
		latex += '\n\\end{document}\n'
		return latex

	@staticmethod
	def save_latex(latex_code, path):
		"""Sauvegarde le code LaTeX dans un fichier."""
		with open(path, 'w', encoding='utf-8') as f:
			f.write(latex_code)

# Exemple d'utilisation (à retirer pour la version bibliothèque) :
# if __name__ == "__main__":
#     generator = LatexGenerator()
#     latex_code = generator.json_file_to_latex('extracted_elements.json')
#     generator.save_latex(latex_code, 'latex_created.tex')


