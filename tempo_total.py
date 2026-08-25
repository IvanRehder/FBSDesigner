#!/usr/bin/env python3
"""
tempo_total.py — Soma o wall_clock_s de todos os _usage.json de um designer,
pra ter um tempo real medido em vez de estimativa. Não usa IA, não gasta API.

Usage:
    python tempo_total.py ai_03           # out/ é assumido
    python tempo_total.py out/ai_03
"""
import json
import sys
from pathlib import Path

DEFAULT_BASE = "out"


def resolve(raw):
    direto = Path(raw)
    if direto.exists():
        return direto
    completado = Path(DEFAULT_BASE) / raw
    if completado.exists():
        return completado
    return None


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python tempo_total.py <designer>")
    d = resolve(sys.argv[1])
    if d is None:
        sys.exit(f"Não achei a pasta pra {sys.argv[1]!r}")

    total_s = 0
    por_requisito = []
    for p in sorted(d.glob("R*_usage.json")):
        data = json.loads(p.read_text())
        s = data.get("totals", {}).get("wall_clock_s")
        if s is not None:
            total_s += s
            por_requisito.append((p.stem.replace("_usage", ""), s))

    if not por_requisito:
        sys.exit("Nenhum _usage.json com wall_clock_s encontrado nessa pasta.")

    print(f"{d.name} — {len(por_requisito)} requisitos com tempo registrado\n")
    for code, s in por_requisito:
        print(f"  {code}: {s/60:.1f} min")

    print(f"\nTotal: {total_s/60:.1f} min ({total_s/3600:.2f} h)")
    print(f"Média por requisito: {(total_s/len(por_requisito))/60:.1f} min")


if __name__ == "__main__":
    main()