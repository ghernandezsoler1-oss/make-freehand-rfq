#!/usr/bin/env python3
"""Validacion estatica de blueprints Make para el proyecto Freehand RFQ.

Uso: python3 tools/validate_blueprint.py blueprints/phase1_rfq_skeleton.json
"""
import json
import re
import sys

# Modulos de escritura prohibidos en fases de solo lectura.
WRITE_PATTERNS = re.compile(
    r"(addRow|updateRow|deleteRow|insertRow|createRow|clearRow|bulkAdd|bulkUpdate|"
    r"ActionSendEmail|sendAnEmail|createSpreadsheet|addSheet|clearValues|updateCell)",
    re.IGNORECASE,
)
# Modulos de IA no permitidos en Fase 1.
AI_PATTERNS = re.compile(r"(openai|anthropic|claude|gemini|ai-|aitools)", re.IGNORECASE)
PLACEHOLDERS = ["GMAIL_CONNECTION", "GMAIL_FOLDER", "GOOGLE_SHEETS_CONNECTION",
                "SPREADSHEET_ID", "SHEET_ID", "RFQ_ID_COLUMN", "RFQ_ID_PATTERN_PENDIENTE"]


def walk(flow, out):
    for m in flow:
        out.append(m)
        for r in m.get("routes", []) or []:
            walk(r.get("flow", []), out)
    return out


def main(path):
    errors = []
    raw = open(path, encoding="utf-8").read()
    bp = json.loads(raw)  # falla si el JSON no es valido

    for key in ("name", "flow", "metadata"):
        if key not in bp:
            errors.append(f"falta clave raiz '{key}'")

    modules = walk(bp["flow"], [])
    ids = [m["id"] for m in modules]
    if len(ids) != len(set(ids)):
        errors.append(f"IDs de modulo duplicados: {ids}")

    for m in modules:
        for key in ("id", "module", "version", "metadata"):
            if key not in m:
                errors.append(f"modulo {m.get('id')}: falta '{key}'")
        name = m.get("module", "")
        if WRITE_PATTERNS.search(name):
            errors.append(f"modulo {m['id']} ({name}) es de ESCRITURA")
        if AI_PATTERNS.search(name):
            errors.append(f"modulo {m['id']} ({name}) es de IA")
        if name == "builtin:BasicRouter":
            routes = m.get("routes", [])
            if len(routes) < 2:
                errors.append(f"router {m['id']}: menos de 2 rutas")
            for i, r in enumerate(routes, 1):
                if not r.get("flow"):
                    errors.append(f"router {m['id']} ruta {i}: flujo vacio")
                elif "filter" not in r["flow"][0]:
                    errors.append(f"router {m['id']} ruta {i}: sin filtro en primer modulo")

    # Referencias {{N.campo}} deben apuntar a modulos que existen y van antes.
    order = {mid: i for i, mid in enumerate(ids)}
    for m in modules:
        text = json.dumps({k: m.get(k) for k in ("mapper", "parameters", "filter")})
        for ref in set(int(x) for x in re.findall(r"[{(;\s](\d+)\.", text)):
            if ref not in order:
                errors.append(f"modulo {m['id']}: referencia a modulo inexistente {ref}")
            elif order[ref] >= order[m["id"]]:
                errors.append(f"modulo {m['id']}: referencia a modulo posterior {ref}")
        feeder = (m.get("parameters") or {}).get("feeder")
        if feeder is not None and feeder not in order:
            errors.append(f"modulo {m['id']}: feeder {feeder} inexistente")

    print(f"Modulos ({len(modules)}):")
    for m in modules:
        label = m.get("metadata", {}).get("designer", {}).get("name", "")
        print(f"  {m['id']:>2}  {m['module']:<35} {label}")
    print("Placeholders pendientes:", [p for p in PLACEHOLDERS if p in raw])

    if errors:
        print("\nERRORES:")
        for e in errors:
            print("  -", e)
        return 1
    print("\nOK: JSON valido, sin modulos de escritura ni IA, referencias coherentes.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
