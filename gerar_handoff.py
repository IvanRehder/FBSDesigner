#!/usr/bin/env python3
"""
gerar_handoff.py — Consolida os requisitos FBS já fechados por um designer
numa espec única, em ordem, pronta pra ele usar de referência ao implementar
as telas no Figma. Determinístico, sem IA, sem custo — só reorganiza o que
já está salvo em {code}.json.

Usage:
    python gerar_handoff.py                # todos os designers de out/
    python gerar_handoff.py ai_03           # só esse designer (out/ é assumido)
    python gerar_handoff.py out/ai_03       # caminho completo também funciona
    python gerar_handoff.py ai_03 --force   # regenera mesmo se já existir
"""

import argparse
import json
import sys
from pathlib import Path

DEFAULT_BASE = "out"


def resolve_base_path(raw_path):
    if raw_path is None:
        base = Path(DEFAULT_BASE)
        return base if base.exists() else None
    direto = Path(raw_path)
    if direto.exists():
        return direto
    completado = Path(DEFAULT_BASE) / raw_path
    if completado.exists():
        return completado
    return None


def load_requirements():
    p = Path("requirements.json")
    if not p.exists():
        sys.exit("requirements.json não encontrado no diretório atual.")
    return json.loads(p.read_text())


def build_handoff(designer_dir, requirements):
    codes = [r["code"] for r in requirements]
    closed, missing = [], []
    for r in requirements:
        p = designer_dir / f"{r['code']}.json"
        if p.exists():
            closed.append(json.loads(p.read_text()))
        else:
            missing.append(r["code"])

    if not closed:
        return None, "nenhum requisito fechado encontrado nessa pasta"

    lines = [f"# FBS — {designer_dir.name}", ""]
    if missing:
        lines.append(f"**⚠ Requisitos ainda não fechados (faltando): {', '.join(missing)}**")
        lines.append("")
    lines.append(f"**Cobertura:** {len(closed)}/{len(codes)} requisitos fechados.")
    lines.append("")
    lines.append("---")
    lines.append("")

    for fbs in closed:
        mods = ", ".join(fbs.get("modalities", []))
        lines.append(f"## {fbs['code']} — {fbs.get('name_en', '')} ({fbs.get('type', '')})")
        lines.append(f"**Modalidades:** {mods}")
        lines.append("")
        lines.append("### Function")
        lines.append(fbs.get("function", "_(vazio)_"))
        lines.append("")
        lines.append("### Behaviour")
        lines.append(fbs.get("behaviour", "_(vazio)_"))
        lines.append("")
        lines.append("### Structure")
        lines.append(fbs.get("structure", "_(vazio)_"))
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines), None


def main():
    parser = argparse.ArgumentParser(description="Consolida requisitos FBS fechados numa espec pra Figma.")
    parser.add_argument("path", nargs="?", default=None,
                         help=f"Pasta {DEFAULT_BASE}/, ou um designer específico (ex.: ai_03). "
                              f"Se omitido, gera pra todo mundo em {DEFAULT_BASE}/.")
    parser.add_argument("--out", default="handoff", help="Pasta de saída (padrão: handoff/)")
    parser.add_argument("--force", action="store_true", help="Regenera mesmo se já existir")
    args = parser.parse_args()

    base = resolve_base_path(args.path)
    if base is None:
        tentativas = [args.path, f"{DEFAULT_BASE}/{args.path}"] if args.path else [DEFAULT_BASE]
        sys.exit("Pasta não encontrada. Tentei: " + ", ".join(tentativas))

    requirements = load_requirements()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if (base / "designer_info.json").exists() or any(base.glob("R*.json")):
        designer_dirs = [base]
    else:
        designer_dirs = [d for d in sorted(base.iterdir()) if d.is_dir()]

    if not designer_dirs:
        sys.exit("Nenhum designer encontrado nessa pasta.")

    for d in designer_dirs:
        out_path = out_dir / f"{d.name}.md"
        if out_path.exists() and not args.force:
            print(f"  já existe {out_path}, pulando (use --force pra regenerar)")
            continue
        print(f"Gerando handoff pra {d.name}...")
        content, err = build_handoff(d, requirements)
        if err:
            print(f"  ⚠ {err}")
            continue
        out_path.write_text(content, encoding="utf-8")
        print(f"  ✓ salvo em {out_path}")


if __name__ == "__main__":
    main()
