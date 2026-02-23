
import re
import json

class LatexParser:
    """
    Convert LaTeX content (file or text) to structured JSON.
    """
    def __init__(self):
        pass

    @staticmethod
    def read_latex_file(path):
        """Read LaTeX file and return its content as string."""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def clean_latex(text):
        """Remove unnecessary LaTeX commands for parsing."""
        return re.sub(r'\\(label|cite|ref|eqref)\{.*?\}', '', text)

    @staticmethod
    def extract_document(text):
        r"""Extract content between \begin{document} and \end{document}."""
        match = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', text, re.DOTALL)
        return match.group(1).strip() if match else ''

    @staticmethod
    def extract_sections(document):
        """Extract sections and their content from the document."""
        section_pattern = r'\\section\*?\{([^}]*)\}(.*?)(?=(\\section\*?\{|$))'
        sections = []
        for m in re.finditer(section_pattern, document, re.DOTALL):
            title = m.group(1).strip()
            content = m.group(2).strip()
            blocks = LatexParser.extract_blocks(content)
            sections.append({'title': title, 'content': content, 'blocks': blocks})
        return sections

    @staticmethod
    def extract_blocks(content):
        """Extract LaTeX environments (blocks) from section content."""
        block_pattern = r'\\begin\{([a-zA-Z*]+)\}(.*?)\\end\{\1\}'
        blocks = []
        last_end = 0
        order = 0
        for b in re.finditer(block_pattern, content, re.DOTALL):
            if b.start() > last_end:
                other_text = content[last_end:b.start()].strip()
                if other_text:
                    blocks.append({
                        'env': 'other',
                        'content': other_text,
                        'order': order
                    })
                    order += 1
            env = b.group(1)
            block_content = b.group(2).strip()
            blocks.append({
                'env': env,
                'content': block_content,
                'order': order
            })
            order += 1
            last_end = b.end()
        if last_end < len(content):
            other_text = content[last_end:].strip()
            if other_text:
                blocks.append({
                    'env': 'other',
                    'content': other_text,
                    'order': order
                })
        return blocks

    def parse_file(self, path):
        """
        Convert a LaTeX file to JSON structure.
        Args:
            path (str): Path to the LaTeX file.
        Returns:
            dict: Parsed JSON structure.
        """
        latex = self.read_latex_file(path)
        latex_cleaned = self.clean_latex(latex)
        document = self.extract_document(latex_cleaned)
        sections = self.extract_sections(document)
        return {'document': {'sections': sections}}

    def parse_text(self, text):
        """
        Convert LaTeX text to JSON structure.
        Args:
            text (str): LaTeX content as string.
        Returns:
            dict: Parsed JSON structure.
        """
        latex_cleaned = self.clean_latex(text)
        document = self.extract_document(latex_cleaned)
        sections = self.extract_sections(document)
        return {'document': {'sections': sections}}

    @staticmethod
    def save_json(data, path):
        """Save JSON data to a file."""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

# Example usage (to remove for library release):
# if __name__ == "__main__":
#     parser = LatexParser()
#     result = parser.parse_file('cours.tex')
#     parser.save_json(result, 'extracted_elements.json')
