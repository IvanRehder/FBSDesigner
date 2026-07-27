import json
from pathlib import Path

OUT = Path("fbs_out")

CTX = {
    "R08":"General","R06":"General",
    "R03":"Operate Aircraft","R01":"Operate Aircraft","R04":"Operate Aircraft","R02":"Operate Aircraft",
    "R05":"Conduct Intelligence and Reconnaissance",
    "R07":"Conduct Surveillance",
    "R09":"Perform UAV Tactical Takeover","R10":"Perform UAV Tactical Takeover",
    "R11":"Control UAVs","R12":"Control UAVs","R13":"Control UAVs",
    "R16":"Employ UAV for ISR Operations","R14":"Employ UAV for ISR Operations","R15":"Employ UAV for ISR Operations",
    "R17":"Employ UAV for Target Tracking","R18":"Employ UAV for Target Tracking",
    "R19":"Conduct UAV Control Handover","R20":"Conduct UAV Control Handover",
}
ORDER = ["R08","R06","R03","R01","R04","R02","R05","R07","R09","R10",
         "R11","R12","R13","R16","R14","R15","R17","R18","R19","R20"]

def load(code):
    p = OUT / f"{code}.json"
    return json.loads(p.read_text()) if p.exists() else None

# agrupa mantendo ordem
groups = {}
for c in ORDER:
    r = load(c)
    if r:
        groups.setdefault(CTX[c], []).append(r)

def esc_tex(s):
    for a,b in [("&","\\&"),("%","\\%"),("_","\\_"),("#","\\#"),
                ("→","$\\to$"),("≈","$\\approx$"),("·","\\textperiodcentered{}"),
                ("≤","$\\leq$"),("≥","$\\geq$"),("×","$\\times$")]:
        s = s.replace(a,b)
    return s

# ---------- Markdown ----------
md = ["# HMI Design Document\n"]
for cap, reqs in groups.items():
    md.append(f"\n## {cap}\n")
    for r in reqs:
        t = "input" if r["type"]=="input" else "output"
        md.append(f"\n### {r['code']} — {r['name_en']} ({t})\n")
        md.append(f"**Modalities:** {' + '.join(r['modalities'])}\n")
        md.append(f"\n**Function.** {r['function']}\n")
        md.append(f"\n**Behaviour.** {r['behaviour']}\n")
        md.append(f"\n**Structure.** {r['structure']}\n")
Path("hmi_design.md").write_text("\n".join(md), encoding="utf-8")

# ---------- LaTeX ----------
tex = [r"\documentclass{article}",
       r"\usepackage[utf8]{inputenc}\usepackage[margin=2.5cm]{geometry}",
       r"\title{HMI Design Document}\begin{document}\maketitle"]
for cap, reqs in groups.items():
    tex.append(r"\section{%s}" % esc_tex(cap))
    for r in reqs:
        t = "input" if r["type"]=="input" else "output"
        tex.append(r"\subsection{%s --- %s (%s)}" % (r["code"], esc_tex(r["name_en"]), t))
        tex.append(r"\textbf{Modalities:} %s\par" % esc_tex(" + ".join(r["modalities"])))
        tex.append(r"\paragraph{Function.} %s" % esc_tex(r["function"]))
        tex.append(r"\paragraph{Behaviour.} %s" % esc_tex(r["behaviour"]))
        tex.append(r"\paragraph{Structure.} %s" % esc_tex(r["structure"]))
tex.append(r"\end{document}")
Path("hmi_design.tex").write_text("\n".join(tex), encoding="utf-8")

print("gerado: hmi_design.md / .tex")