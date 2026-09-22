#!/usr/bin/env python3
"""
gerar_handoff.py — Gera o handoff de um designer agrupado por
artefato/componente de interface (não por requisito), pra servir de
referência pronta pra montar as telas no Figma.

O agrupamento por componente exige reconhecer reuso semântico entre
requisitos (o mesmo painel descrito/estendido em textos diferentes) —
isso não dá pra fazer por correspondência de string. Por isso o processo
tem duas etapas: uma chamada de LLM identifica e descreve os componentes
(salva num JSON intermediário, inspecionável e reproduzível sem rechamar
o modelo), e uma etapa determinística renderiza o markdown final a
partir desse JSON.

Requisitos sem Structure fechada ficam de fora dos componentes e entram
numa lista de pendências no topo do documento.

Setup:
    pip install anthropic python-dotenv
    export ANTHROPIC_API_KEY=sk-...
    (ou cria um arquivo .env na mesma pasta com a linha ANTHROPIC_API_KEY=sk-...)

Usage:
    python tools/gerar_handoff.py ai_98            # só esse designer
    python tools/gerar_handoff.py                  # todo mundo em out/
    python tools/gerar_handoff.py ai_98 --force     # regenera mesmo se já existir
"""

import argparse
import json
import os
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-opus-4-8"  # agrupar por componente exige julgamento semântico real, não é tarefa mecânica
DEFAULT_BASE = "out"

PROMPT_PATH = Path(__file__).parent / "gerar_handoff_prompt.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")


def resolve_base_path(raw_path):
    """Decide qual pasta usar — mesma lógica do avaliar_fbs.py."""
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
    p = Path("content/requirements.json")
    if not p.exists():
        sys.exit("requirements.json não encontrado no diretório atual.")
    return {r["code"]: r for r in json.loads(p.read_text(encoding="utf-8"))}


def split_complete_pending(designer_dir, requirements):
    """Separa requisitos com Structure fechada (entram nos componentes) dos
    que não têm (viram pendência, com o motivo). A regra de completude é
    só a Structure — Function/Behaviour sozinhos não bastam pra desenhar
    a tela."""
    complete, pending = [], []
    for code, req in requirements.items():
        p = designer_dir / f"{code}.json"
        if not p.exists():
            pending.append((code, req, "não fechado"))
            continue
        fbs = json.loads(p.read_text(encoding="utf-8"))
        if not fbs.get("structure", "").strip():
            reason = ("só Function" if not fbs.get("behaviour", "").strip()
                      else "Behaviour ok, Structure vazia")
            pending.append((code, req, reason))
            continue
        complete.append(fbs)
    complete.sort(key=lambda f: f["code"])
    pending.sort(key=lambda t: t[0])
    return complete, pending


def call_llm(client, complete):
    payload = [
        {
            "code": f["code"], "name_en": f["name_en"], "type": f["type"],
            "modalities": f["modalities"],
            "function": f["function"], "behaviour": f["behaviour"], "structure": f["structure"],
        }
        for f in complete
    ]
    resp = client.messages.create(
        model=MODEL, max_tokens=8000, output_config={"effort": "high"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": json.dumps(payload, ensure_ascii=False, indent=2)}],
    )
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    return json.loads(raw)


def render_markdown(designer_name, requirements, components, pending):
    total = len(requirements)
    done = total - len(pending)
    lines = [f"# FBS → Figma — {designer_name}", ""]
    lines.append(f"**Cobertura:** {done}/{total} requisitos com Structure fechada.")
    lines.append("")
    lines.append("## Requisitos")
    lines.append("")
    for code, req in requirements.items():
        mods = ", ".join(req.get("modalities", []))
        lines.append(f"- **{code}** — {req['name_en']} ({mods})")
    lines.append("")
    if pending:
        lines.append("## ⚠ Pendências (Structure não definida — não entram no handoff)")
        for code, req, reason in pending:
            lines.append(f"- **{code}** — {req['name_en']} ({reason})")
        lines.append("")
    lines.append("## Componentes")
    lines.append("")
    for i, comp in enumerate(components, start=1):
        codes = comp["requirements"]
        mods = sorted({m for c in codes for m in requirements.get(c, {}).get("modalities", [])})
        lines.append(f"### {i}. {comp['name']}")
        lines.append(f"**Requisitos:** {', '.join(codes)} · **Modalidades:** {', '.join(mods)}")
        lines.append("")
        lines.append(comp["description"])
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Consolida requisitos FBS fechados por componente de interface, pra handoff de Figma.")
    parser.add_argument("path", nargs="?", default=None,
                         help=f"Pasta {DEFAULT_BASE}/, ou um designer específico (ex.: ai_98). "
                              f"Se omitido, roda pra todo mundo em {DEFAULT_BASE}/.")
    parser.add_argument("--out", default="handoff", help="Pasta de saída (padrão: handoff/)")
    parser.add_argument("--force", action="store_true", help="Regenera mesmo se já existir")
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit(
            "ANTHROPIC_API_KEY não encontrada.\n"
            "Configura de um dos dois jeitos, na mesma pasta de onde você roda este script:\n"
            "  export ANTHROPIC_API_KEY=sk-...\n"
            "ou cria um arquivo .env com a linha:\n"
            "  ANTHROPIC_API_KEY=sk-..."
        )

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

    client = anthropic.Anthropic()

    for d in designer_dirs:
        md_path = out_dir / f"{d.name}.md"
        if md_path.exists() and not args.force:
            print(f"⏭  {d.name}: já existe {md_path}, pulando (use --force pra regenerar)")
            continue

        complete, pending = split_complete_pending(d, requirements)
        if not complete:
            print(f"⚠ {d.name}: nenhum requisito com Structure fechada, pulando")
            continue

        print(f"Consolidando {d.name} ({len(complete)} completos, {len(pending)} pendentes)...")
        try:
            components = call_llm(client, complete)
        except (json.JSONDecodeError, anthropic.APIError) as e:
            print(f"  ⚠ falhou pra {d.name}: {e}")
            continue

        components_path = out_dir / f"{d.name}_components.json"
        components_path.write_text(json.dumps(components, indent=2, ensure_ascii=False), encoding="utf-8")

        content = render_markdown(d.name, requirements, components, pending)
        md_path.write_text(content, encoding="utf-8")
        print(f"  ✓ {len(components)} componentes → {md_path} (dados brutos em {components_path})")


if __name__ == "__main__":
    main()
