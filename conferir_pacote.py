#!/usr/bin/env python3
"""
conferir_pacote.py — Confere se uma pasta (a que vai virar o zip/branch pro
designer) tem todos os arquivos necessários, antes de mandar pra alguém e
descobrir depois que faltou algo.

Usage:
    python conferir_pacote.py /caminho/da/pasta
"""
import sys
from pathlib import Path

REQUIRED_COMMON = [
    "requirements.txt", "requirements.json", "intro_text.md", "mumt_text.md",
    "example_text.md", "layer_hints.json", "designer_fields.json",
    "toy_requirement.json", "screens.json",
]

REQUIRED_AI = [
    "app_streamlit.py", "fbs_core_ai.py", "mechanics_ai.md",
    "iniciar_ia.sh", "iniciar_ia.bat",
    "system_description.txt", "hmi_baseline.txt", "response_style.txt",
]

REQUIRED_HUMAN = [
    "app_streamlit_human.py", "fbs_core_human.py", "mechanics_human.md",
    "iniciar_human.sh", "iniciar_human.bat",
]


def check(base, required, label):
    missing = [f for f in required if not (base / f).exists()]
    print(f"--- {label} ---")
    if missing:
        for f in missing:
            print(f"  \u2717 FALTANDO: {f}")
    else:
        print("  \u2713 tudo presente")
    return missing


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python conferir_pacote.py <pasta>")
    base = Path(sys.argv[1])
    if not base.exists():
        sys.exit(f"Pasta não encontrada: {base}")

    all_missing = []
    all_missing += check(base, REQUIRED_COMMON, "Comum às duas condições")
    all_missing += check(base, REQUIRED_AI, "Condição IA")
    all_missing += check(base, REQUIRED_HUMAN, "Condição Human")

    screens_dir = base / "screens"
    print("--- Pasta de telas ---")
    if not screens_dir.exists() or not any(screens_dir.iterdir()):
        print("  \u2717 pasta screens/ ausente ou vazia")
        all_missing.append("screens/*")
    else:
        n = len(list(screens_dir.iterdir()))
        print(f"  \u2713 {n} arquivo(s) em screens/")

    print()
    if all_missing:
        print(f"FALTANDO {len(all_missing)} item(ns) — não manda esse pacote ainda.")
        sys.exit(1)
    print("Pacote completo.")


if __name__ == "__main__":
    main()