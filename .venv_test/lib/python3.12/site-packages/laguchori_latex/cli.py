from __future__ import annotations

from pathlib import Path
import json
import argparse

from .parser import LatexParser
from .generator import LatexGenerator


def _cmd_parse(args: argparse.Namespace) -> int:
    parser = LatexParser()
    data = parser.parse_file(args.input)

    out = Path(args.output) if args.output else Path(args.input).with_suffix(".json")
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0


def _cmd_generate(args: argparse.Namespace) -> int:
    gen = LatexGenerator(preamble_path=args.preamble)
    latex = gen.json_file_to_latex(args.input)

    out = Path(args.output) if args.output else Path(args.input).with_suffix(".tex")
    out.write_text(latex, encoding="utf-8")
    return 0


def app() -> None:
    p = argparse.ArgumentParser(prog="laguchori-latex", description="LaTeX <-> JSON tools")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_parse = sub.add_parser("parse", help="Parse LaTeX file -> JSON")
    p_parse.add_argument("input", help="Path to .tex file")
    p_parse.add_argument("-o", "--output", help="Output JSON path (default: input.json)")
    p_parse.set_defaults(func=_cmd_parse)

    p_gen = sub.add_parser("generate", help="Generate LaTeX from JSON file")
    p_gen.add_argument("input", help="Path to .json file")
    p_gen.add_argument("-o", "--output", help="Output TeX path (default: input.tex)")
    p_gen.add_argument("--preamble", default="preambule.tex", help="Path to preamble file")
    p_gen.set_defaults(func=_cmd_generate)

    args = p.parse_args()
    raise SystemExit(args.func(args))