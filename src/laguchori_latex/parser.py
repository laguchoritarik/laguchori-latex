import re
import json
from typing import List, Dict, Optional, Tuple

class LatexParser:
    """
    Convert LaTeX content (file or text) to structured JSON.
    Supports:
    - \section, \subsection, \subsubsection hierarchy
    - environments with optional [title]
    - nested environments (stack-based)
    - optional cleaning of refs/labels/cites
    """

    # -------- Patterns for document extraction --------
    DOC_RE = re.compile(r'\\begin\{document\}(.*?)\\end\{document\}', re.DOTALL)

    # -------- Patterns for headings --------
    SECTION_RE = re.compile(r'\\section\*?\{([^}]*)\}')
    SUBSECTION_RE = re.compile(r'\\subsection\*?\{([^}]*)\}')
    SUBSUBSECTION_RE = re.compile(r'\\subsubsection\*?\{([^}]*)\}')

    # -------- Environment begin/end (captures optional [..]) --------
    BEGIN_ENV_RE = re.compile(r'\\begin\{([a-zA-Z*]+)\}(\[[^\]]*\])?', re.DOTALL)
    END_ENV_RE   = re.compile(r'\\end\{([a-zA-Z*]+)\}', re.DOTALL)

    # Label extractor (kept!)
    LABEL_RE = re.compile(r'\\label\{([^}]*)\}')

    def __init__(self, strip_refs: bool = False):
        self.strip_refs = strip_refs

    @staticmethod
    def read_latex_file(path: str) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def clean_latex(self, text: str) -> str:
        """
        Optional: remove \cite/\ref/\eqref while KEEPING \label (or keep all).
        Default: keep everything.
        """
        if not self.strip_refs:
            return text
        # remove cite/ref/eqref only
        return re.sub(r'\\(cite|ref|eqref)\{.*?\}', '', text)

    @classmethod
    def extract_document(cls, text: str) -> str:
        m = cls.DOC_RE.search(text)
        return m.group(1).strip() if m else text.strip()

    # -----------------------------
    # 1) Split document into heading blocks (section/subsection/subsubsection)
    # -----------------------------
    @classmethod
    def _iter_headings(cls, doc: str) -> List[Tuple[int, str, str]]:
        """
        Returns list of (pos, level, title)
        level in {"section","subsection","subsubsection"}
        """
        items = []
        for m in cls.SECTION_RE.finditer(doc):
            items.append((m.start(), "section", m.group(1).strip()))
        for m in cls.SUBSECTION_RE.finditer(doc):
            items.append((m.start(), "subsection", m.group(1).strip()))
        for m in cls.SUBSUBSECTION_RE.finditer(doc):
            items.append((m.start(), "subsubsection", m.group(1).strip()))
        items.sort(key=lambda x: x[0])
        return items

    @classmethod
    def extract_sections(cls, document: str) -> List[Dict]:
        """
        Build hierarchical structure:
        sections -> subsections -> subsubsections
        Each node has 'title', 'content', 'blocks'
        """
        headings = cls._iter_headings(document)
        if not headings:
            # No headings: treat whole doc as one pseudo-section
            blocks = cls.extract_blocks(document)
            return [{"title": "", "content": document.strip(), "blocks": blocks, "subsections": []}]

        # Helper to slice content between heading positions
        def slice_between(i: int) -> str:
            start = headings[i][0]
            end = headings[i+1][0] if i+1 < len(headings) else len(document)
            return document[start:end]

        # We will construct a tree using stacks
        root_sections: List[Dict] = []
        current_section: Optional[Dict] = None
        current_subsection: Optional[Dict] = None

        for i, (pos, level, title) in enumerate(headings):
            chunk = slice_between(i)

            # Remove the heading command line itself from the node content
            if level == "section":
                chunk_body = cls.SECTION_RE.sub("", chunk, count=1).strip()
                node = {
                    "title": title,
                    "content": chunk_body,
                    "blocks": cls.extract_blocks(chunk_body),
                    "subsections": []
                }
                root_sections.append(node)
                current_section = node
                current_subsection = None

            elif level == "subsection":
                chunk_body = cls.SUBSECTION_RE.sub("", chunk, count=1).strip()
                node = {
                    "title": title,
                    "content": chunk_body,
                    "blocks": cls.extract_blocks(chunk_body),
                    "subsubsections": []
                }
                if current_section is None:
                    # orphan subsection: attach to pseudo section
                    pseudo = {
                        "title": "",
                        "content": "",
                        "blocks": [],
                        "subsections": []
                    }
                    root_sections.append(pseudo)
                    current_section = pseudo
                current_section["subsections"].append(node)
                current_subsection = node

            elif level == "subsubsection":
                chunk_body = cls.SUBSUBSECTION_RE.sub("", chunk, count=1).strip()
                node = {
                    "title": title,
                    "content": chunk_body,
                    "blocks": cls.extract_blocks(chunk_body)
                }
                if current_subsection is None:
                    # orphan subsubsection: attach to pseudo subsection
                    if current_section is None:
                        pseudo_sec = {"title": "", "content": "", "blocks": [], "subsections": []}
                        root_sections.append(pseudo_sec)
                        current_section = pseudo_sec
                    pseudo_sub = {"title": "", "content": "", "blocks": [], "subsubsections": []}
                    current_section["subsections"].append(pseudo_sub)
                    current_subsection = pseudo_sub
                current_subsection["subsubsections"].append(node)

        return root_sections

    # -----------------------------
    # 2) Extract blocks using stack-based environment parsing
    # -----------------------------
    @classmethod
    def extract_blocks(cls, content: str) -> List[Dict]:
        """
        Extract LaTeX environments robustly (nested) using a stack.
        Also captures optional begin option: \begin{theorem}[Title]
        Returns list of blocks and 'other' text between them.
        """
        blocks: List[Dict] = []
        order = 0

        # Find all begin/end tokens
        tokens = []
        for m in cls.BEGIN_ENV_RE.finditer(content):
            tokens.append((m.start(), "begin", m.group(1), m.group(2)))
        for m in cls.END_ENV_RE.finditer(content):
            tokens.append((m.start(), "end", m.group(1), None))
        tokens.sort(key=lambda x: x[0])

        if not tokens:
            other_text = content.strip()
            if other_text:
                blocks.append({"env": "other", "content": other_text, "order": order})
            return blocks

        stack = []
        last_emit = 0  # where "other" text begins

        for idx, (pos, kind, env, opt) in enumerate(tokens):
            if kind == "begin":
                if not stack:
                    # emit other text before first top-level env
                    other = content[last_emit:pos].strip()
                    if other:
                        blocks.append({"env": "other", "content": other, "order": order})
                        order += 1
                    last_emit = pos
                stack.append((env, pos, opt))

            else:  # end
                if not stack:
                    continue
                top_env, top_pos, top_opt = stack[-1]
                if top_env != env:
                    # mismatched end; ignore (best-effort)
                    continue

                stack.pop()
                if not stack:
                    # closed a top-level environment: slice it
                    end_match = cls.END_ENV_RE.match(content, pos)
                    end_end = end_match.end() if end_match else pos

                    full_block = content[top_pos:end_end].strip()

                    # Extract inner content between \begin{env}[opt] and \end{env}
                    begin_match = cls.BEGIN_ENV_RE.match(content, top_pos)
                    begin_end = begin_match.end() if begin_match else top_pos

                    inner = content[begin_end:pos].strip()

                    # Optional title like [Riesz]
                    title = None
                    if top_opt:
                        title = top_opt.strip()[1:-1].strip()  # remove [ ]
                    # Label (if exists)
                    label_m = cls.LABEL_RE.search(inner)
                    label = label_m.group(1).strip() if label_m else None

                    blocks.append({
                        "env": top_env,
                        "title": title,
                        "label": label,
                        "content": inner,
                        "order": order
                    })
                    order += 1
                    last_emit = end_end

        # tail other text
        tail = content[last_emit:].strip()
        if tail:
            blocks.append({"env": "other", "content": tail, "order": order})

        return blocks

    # -------- Public API --------
    def parse_file(self, path: str) -> Dict:
        latex = self.read_latex_file(path)
        latex_cleaned = self.clean_latex(latex)
        document = self.extract_document(latex_cleaned)
        sections = self.extract_sections(document)
        return {"document": {"sections": sections}}

    def parse_text(self, text: str) -> Dict:
        latex_cleaned = self.clean_latex(text)
        document = self.extract_document(latex_cleaned)
        sections = self.extract_sections(document)
        return {"document": {"sections": sections}}

    @staticmethod
    def save_json(data: Dict, path: str) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)