# Freehand RFQ – Automatización Make.com

Construcción incremental, fase por fase. Cada fase se valida en Make antes de avanzar.

| Fase | Estado | Archivo |
|---|---|---|
| 1. Gmail → RFQ ID → Google Sheets → Router (solo lectura) | En prueba | `blueprints/phase1_rfq_skeleton.json` |

## Validación estática

```bash
python3 tools/validate_blueprint.py blueprints/phase1_rfq_skeleton.json
```

Comprueba: JSON válido, IDs únicos, ningún módulo de escritura ni de IA, rutas del router
con filtro y referencias `{{N.campo}}` que apuntan a módulos anteriores existentes.

## Placeholders a reemplazar en Make

| Placeholder | Dónde | Qué poner |
|---|---|---|
| `GMAIL_CONNECTION` | Módulo 1 | Conexión Gmail del buzón compartido |
| `GMAIL_FOLDER` | Módulo 1 | Carpeta/etiqueta (ej. INBOX) |
| `RFQ_ID_PATTERN_PENDIENTE_(\S+)` | Módulo 2 | Regex real del RFQ ID (pendiente de ejemplos reales) |
| `GOOGLE_SHEETS_CONNECTION` | Módulo 4 | Conexión Google Sheets |
| `SPREADSHEET_ID` / `SHEET_ID` | Módulo 4 | Hoja de RFQs |
| `RFQ_ID_COLUMN` | Módulo 4 | Columna que contiene el RFQ ID |
