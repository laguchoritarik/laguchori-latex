# laguchori_latex/cleaner.py
# -*- coding: utf-8 -*-

import re
import unicodedata
from dataclasses import dataclass
from typing import Optional, Dict, List

def _slugify(s: str) -> str:
    s = (s or "").strip()
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s or "x"

# --------------------------
# Patterns
# --------------------------
_SECTION_RE = re.compile(r"^\s*\\(section|subsection|subsubsection)\*?\{", re.UNICODE)

# Roman numerals: I, II, III, IV, V, VI, VII, VIII, IX, X, ...
_ROMAN_RE = r"(?:M{0,4}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3}))"

_SECTION_STRIP_NUM_RE = re.compile(
    rf"""^(\s*\\(section|subsection|subsubsection)\*?\{{)\s*
         (?:
            (?P<arabic>\d+(?:\.\d+)*) |        # 2, 2.1, 3.4.5
            (?P<roman>{_ROMAN_RE})             # VI, IX, etc.
         )
         \s+ (?P<title>[^}}]*) \}}\s*$""",
    re.VERBOSE | re.UNICODE,
)
_BOLD_NUMBERED_TITLE_RE = re.compile(
    r"""^\s*\\textbf\{\s*(?P<num>\d+(?:\.\d+)*)\s+(?P<title>[^}]*)\}\s*$""",
    re.UNICODE,
)
_BOLD_BLOCK_HEAD_RE = re.compile(
    r"""^\s*\\textbf\{\s*(?P<head>Notations?|Exemples?|Remarques?)\s*:\s*\}\s*$""",
    re.UNICODE,
)

_KIND_WORDS = r"(Théorème|Theoreme|Proposition|Lemme|Corollaire|Définition|Definition|Exemple|Example)"
_STMT_HEADER_RE = re.compile(
    rf"""
    ^\s*
    (?:\\textbf\{{|\\textit\{{)?\s*
    (?P<kind>{_KIND_WORDS})\s*
    (?P<num>\d+)?\s*
    (?:\((?P<title>[^)]*)\))?\s*
    [\.:]\s*
    (?:\}}\s*)?
    (?P<rest>.*?)
    \s*$
    """,
    re.VERBOSE | re.UNICODE,
)

_PROOF_MARK_RE = re.compile(
    r"""
    ^\s*
    (?:\\textit\{|\\textbf\{)?\s*
    (Démonstration|Demonstration|Preuve|Proof)
    (?:\s+\d+)?                      
    (?:\s+de\s+la\s+.*)?             
    \s*[\.:]\s*
    (?:\}\s*)?
    (?P<rest>.*?)
    \s*$
    """,
    re.VERBOSE | re.UNICODE,
)

_REMARK_MARK_RE = re.compile(
    r"""
    ^\s*
    (?:\\textbf\{|\\textit\{)?\s*
    (Remarque|Remark|Variante|Variant)
    \s*[\.:]\s*
    (?:\}\s*)?
    (?P<rest>.*?)
    \s*$
    """,
    re.VERBOSE | re.UNICODE,
)

_KIND_MAP = {
    "Théorème": ("theorem", "thm"),
    "Theoreme": ("theorem", "thm"),
    "Proposition": ("proposition", "prop"),
    "Lemme": ("lemma", "lem"),
    "Corollaire": ("corollary", "cor"),
    "Définition": ("definition", "def"),
    "Definition": ("definition", "def"),
    "Exemple": ("example", "ex"),
    "Example": ("example", "ex"),
}

@dataclass
class _OpenEnv:
    env: str
    title: Optional[str] = None
    label: Optional[str] = None

def _env_begin(e: _OpenEnv) -> str:
    opt = f"[{e.title}]" if e.title else ""
    lab = f"\\label{{{e.label}}}\n" if e.label else ""
    return f"\\begin{{{e.env}}}{opt}\n{lab}"

def _env_end(env: str) -> str:
    return f"\\end{{{env}}}\n"

def _next_label(prefix: str, counters: Dict[str, int], title: Optional[str], add_labels: bool) -> Optional[str]:
    if not add_labels:
        return None
    if title and title.strip():
        return f"{prefix}:{_slugify(title)}"
    counters[prefix] = counters.get(prefix, 0) + 1
    return f"{prefix}:{counters[prefix]}"

def clean_text(
    text: str,
    *,
    add_labels: bool = True,
    strip_numeric_prefix_in_sections: bool = True,
) -> str:
    """
    Nettoie un LaTeX OCR en LaTeX "clean":
    - \textbf{2 Titre} -> \section{Titre} (niveau selon 2 / 2.1 / 2.1.3)
    - \section{3 Titre} -> \section{Titre} (si strip_numeric_prefix_in_sections=True)
    - Théorème/Prop/Lemme/... -> environnements
    - Démonstration -> proof, Remarque/Variante -> remark
    - \textbf{Notations :} -> notation, \textbf{Exemples :} -> examples
    """
    lines = text.replace("\r\n", "\n").split("\n")
    out: List[str] = []
    current: Optional[_OpenEnv] = None
    counters: Dict[str, int] = {}

    def close_current():
        nonlocal current
        if current is not None:
            out.append(_env_end(current.env))
            current = None

    def open_env_stmt(kind: str, title: Optional[str], rest: str):
        nonlocal current
        close_current()
        env, prefix = _KIND_MAP.get(kind, ("theorem", "thm"))
        label = _next_label(prefix, counters, title, add_labels)
        current = _OpenEnv(env=env, title=title, label=label)
        out.append(_env_begin(current))
        if rest:
            out.append(rest)

    def open_env_simple(env: str, rest: str = "", title: Optional[str] = None):
        nonlocal current
        close_current()
        current = _OpenEnv(env=env, title=title, label=None)
        out.append(_env_begin(current))
        if rest:
            out.append(rest)

    for line in lines:
        # Existing LaTeX sections
        if _SECTION_RE.match(line):
            close_current()
            msec = _SECTION_STRIP_NUM_RE.match(line)
            if msec and msec.group("title").strip():
                prefix = msec.group(1)  # \section{ ou \subsection{ ...
                title = msec.group("title").strip()
                out.append(f"{prefix}{title}}}")
            else:
                out.append(line)
            continue

        # OCR bold numbered titles -> sections
        nt = _BOLD_NUMBERED_TITLE_RE.match(line)
        if nt:
            close_current()
            num = nt.group("num").strip()
            title = nt.group("title").strip()
            depth = num.count(".") + 1
            if depth == 1:
                out.append(f"\\section{{{title}}}")
            elif depth == 2:
                out.append(f"\\subsection{{{title}}}")
            else:
                out.append(f"\\subsubsection{{{title}}}")
            continue

        # Notations / Exemples block heads
        bh = _BOLD_BLOCK_HEAD_RE.match(line)
        if bh:
            head = bh.group("head").strip().lower()

            if head.startswith("notat"):
                open_env_simple("notation")
            elif head.startswith("exem"):
                open_env_simple("examples")
            else:
                # "Remarque:" ou "Remarques:"
                open_env_simple("remark")
            continue

        # Statement headers
        m = _STMT_HEADER_RE.match(line)
        if m:
            kind = m.group("kind")
            title = m.group("title")
            rest = (m.group("rest") or "").strip()
            if kind not in _KIND_MAP and kind.lower() == "theoreme":
                kind = "Theoreme"
            open_env_stmt(kind, title, rest)
            continue

        # Proof marker
        pm = _PROOF_MARK_RE.match(line)
        if pm:
            rest = (pm.group("rest") or "").strip()
            open_env_simple("proof", rest=rest)
            continue

        # Remark / Variant
        rm = _REMARK_MARK_RE.match(line)
        if rm:
            rest = (rm.group("rest") or "").strip()
            open_env_simple("remark", rest=rest)
            continue

        out.append(line)

    close_current()
    return "\n".join(out)

def clean_file(
    input_path: str,
    output_path: str,
    *,
    add_labels: bool = True,
    strip_numeric_prefix_in_sections: bool = True,
) -> None:
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()
    cleaned = clean_text(
        text,
        add_labels=add_labels,
        strip_numeric_prefix_in_sections=strip_numeric_prefix_in_sections,
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned)