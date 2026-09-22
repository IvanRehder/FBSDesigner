#!/usr/bin/env python3
"""
avaliar_fbs.py — Avalia automaticamente os requisitos fechados de cada
designer, usando um LLM juiz, com o mesmo rubrico do prompt_avaliacao_fbs.md.
Também soma o tempo real gasto (wall_clock_s de cada Rxx_usage.json, sem
custo de API) e coloca esse resumo no topo do mesmo relatório — antes esse
cálculo vivia em tempo_total.py, separado; foi incorporado aqui.

Roda OFFLINE, fora dos apps do Streamlit — o pesquisador executa manualmente
depois de baixar os dados (zip do admin, pasta local, ou merge de branch).
Não importa fbs_core_ai/fbs_core_human de propósito: esses dois agora
dependem de st.session_state (pro fix do bug de designer compartilhado),
que só existe dentro de um app Streamlit rodando de verdade.

Setup:
    pip install anthropic python-dotenv
    export ANTHROPIC_API_KEY=sk-...
    (ou cria um arquivo .env na mesma pasta com a linha ANTHROPIC_API_KEY=sk-...)

Precisa do arquivo eval_prompt.md na mesma pasta — é onde fica o texto do
rubrico de avaliação, editável sem mexer neste .py.

Usage:
    python avaliar_fbs.py                          # avalia todos os designers de out/
    python avaliar_fbs.py ai_03                     # avalia só esse designer (out/ é assumido)
    python avaliar_fbs.py out/ai_03                 # caminho completo também funciona
    python avaliar_fbs.py --out outra_pasta/         # muda a pasta de saída (padrão: report/)
"""

import argparse
import json
import os
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-opus-4-8"
DEFAULT_BASE = "out"  # muda aqui se um dia renomear a pasta padrão de novo

EVAL_PROMPT_PATH = Path(__file__).parent / "eval_prompt.md"
SYSTEM_PROMPT = EVAL_PROMPT_PATH.read_text(encoding="utf-8")


def resolve_base_path(raw_path):
    """Decide qual pasta usar:
    - sem argumento nenhum -> DEFAULT_BASE (ex.: 'out')
    - argumento que já existe como caminho -> usa direto
    - argumento que não existe sozinho, mas existe dentro de DEFAULT_BASE -> completa
    Retorna None se nada bater, pra quem chamou decidir a mensagem de erro."""
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
    return json.loads(p.read_text())


def collect_designer_data(designer_dir, codes):
    """Só os arquivos {code}.json de requisitos reais — ignora toy, backups
    _prevN, sus.json, designer_info.json etc."""
    items = []
    for code in sorted(codes):
        p = designer_dir / f"{code}.json"
        if p.exists():
            items.append(json.loads(p.read_text()))
    return items


def resumo_tempo(designer_dir):
    """Soma o wall_clock_s de todos os Rxx_usage.json do designer — tempo
    real medido, sem gastar API (não depende do LLM avaliador). Retorna
    None se não houver nenhum _usage.json com tempo registrado."""
    total_s = 0
    por_requisito = []
    for p in sorted(designer_dir.glob("R*_usage.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        s = data.get("totals", {}).get("wall_clock_s")
        if s is not None:
            total_s += s
            por_requisito.append((p.stem.replace("_usage", ""), s))
    if not por_requisito:
        return None

    lines = ["## Tempo gasto", ""]
    for code, s in por_requisito:
        lines.append(f"- {code}: {s / 60:.1f} min")
    lines.append("")
    lines.append(
        f"**Total:** {total_s / 60:.1f} min ({total_s / 3600:.2f} h) · "
        f"**Média por requisito:** {(total_s / len(por_requisito)) / 60:.1f} min"
    )
    lines.append("\n---\n")
    return "\n".join(lines)


def evaluate_designer(client, designer_dir, requirements):
    codes = {r["code"] for r in requirements}
    closed = collect_designer_data(designer_dir, codes)
    if not closed:
        return None, "nenhum requisito fechado encontrado nessa pasta"

    payload = {
        "requirements_do_projeto": requirements,
        "requisitos_fechados_pelo_designer": closed,
    }
    resp = client.messages.create(
        model=MODEL,
        max_tokens=10000,
        output_config={"effort": "high"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": json.dumps(payload, ensure_ascii=False, indent=2)}],
    )
    text = resp.content[0].text
    if resp.stop_reason == "max_tokens":
        text += (
            "\n\n---\n"
            "**AVISO: esta avaliação foi CORTADA antes de terminar** "
            "(estourou o limite de tokens da resposta). Não conte com o "
            "conteúdo depois do último requisito completo — aumenta o "
            "max_tokens no script e roda de novo pra esse designer."
        )
    return text, None


def main():
    parser = argparse.ArgumentParser(description="Avalia requisitos FBS fechados por designer(es).")
    parser.add_argument("path", nargs="?", default=None,
                         help=f"Pasta {DEFAULT_BASE}/, ou um designer específico (ex.: ai_03). "
                              f"Se omitido, avalia todo mundo em {DEFAULT_BASE}/.")
    parser.add_argument("--out", default="report", help="Pasta de saída dos relatórios (padrão: report/)")
    parser.add_argument("--force", action="store_true",
                         help="Refaz mesmo quem já tem relatório salvo (por padrão, pula)")
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

    client = anthropic.Anthropic()

    # 'path' pode ser a pasta de UM designer (tem R*.json direto nela)
    # ou a pasta-mãe com uma subpasta por designer
    if (base / "designer_info.json").exists() or any(base.glob("R*.json")):
        designer_dirs = [base]
    else:
        designer_dirs = [d for d in sorted(base.iterdir()) if d.is_dir()]

    if not designer_dirs:
        sys.exit("Nenhum designer encontrado nessa pasta.")

    for d in designer_dirs:
        out_path = out_dir / f"{d.name}.md"
        if out_path.exists() and not args.force:
            print(f"⏭  {d.name}: já tem relatório em {out_path}, pulando (usa --force pra refazer)")
            continue

        print(f"Avaliando {d.name}...")
        report, err = evaluate_designer(client, d, requirements)
        if err:
            print(f"  ⚠ {err}")
            continue
        tempo = resumo_tempo(d)
        if tempo:
            report = tempo + "\n" + report
        out_path.write_text(report, encoding="utf-8")
        if "AVISO: esta avaliação foi CORTADA" in report:
            print(f"  ⚠ salvo em {out_path} — MAS FOI CORTADA, veja o aviso no final do arquivo")
        else:
            print(f"  ✓ salvo em {out_path}")


if __name__ == "__main__":
    main()
