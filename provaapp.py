
import json
import requests

# ============================================================
# CONFIGURAZIONE VAVOO - CATALOGO COMPLETO
# ============================================================

VAVOO_CATALOG_URL = "https://vavoo.to/live/catalog/live/channels.json"

VAVOO_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, */*",
    "Accept-Language": "it",
    "Referer": "https://vavoo.to/",
}

# ============================================================
# SCARICA IL CATALOGO SENZA FILTRI
# ============================================================

print("=" * 60)
print("SCARICAMENTO CATALOGO VAVOO COMPLETO")
print("=" * 60)

try:
    response = requests.get(
        VAVOO_CATALOG_URL,
        headers=VAVOO_HEADERS,
        timeout=30
    )
    response.raise_for_status()
    catalog_data = response.json()


print("Tipo risposta:", type(catalog_data).__name__)

if isinstance(catalog_data, dict):
    print("Chiavi risposta:", list(catalog_data.keys()))
    print("nextCursor:", catalog_data.get("nextCursor"))
    print("cursor:", catalog_data.get("cursor"))

print("Elementi estratti:", len(
    catalog_data if isinstance(catalog_data, list)
    else catalog_data.get("items", catalog_data.get("channels", []))
    if isinstance(catalog_data, dict)
    else []
))


except Exception as e:
    raise SystemExit(f"Errore durante il download del catalogo: {e}")

if isinstance(catalog_data, list):
    vavoo_items = catalog_data

elif isinstance(catalog_data, dict):
    vavoo_items = (
        catalog_data.get("items", [])
        or catalog_data.get("channels", [])
    )

    if not vavoo_items and isinstance(catalog_data.get("data"), list):
        vavoo_items = catalog_data["data"]

else:
    vavoo_items = []

# ============================================================
# MOSTRA TUTTI I NOMI RESTITUITI
# ============================================================

print(f"\nElementi ricevuti: {len(vavoo_items)}\n")

for numero, item in enumerate(vavoo_items, start=1):
    if not isinstance(item, dict):
        continue

    print(
        f"{numero}. "
        f"NOME: {item.get('name', '')} | "
        f"ID: {item.get('id', '')} | "
        f"URL: {item.get('url', '')}"
    )

print("\n" + "=" * 60)
print("FINE CATALOGO")
print(f"Totale elementi ricevuti: {len(vavoo_items)}")
print("=" * 60)
