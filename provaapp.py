
import json
import requests

# ============================================================
# CONFIGURAZIONE VAVOO
# ============================================================

VAVOO_CATALOG_URL = "https://vavoo.to/live/catalog/live/channels.json"

VAVOO_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, */*",
    "Accept-Language": "it",
    "Referer": "https://vavoo.to/",
}

# ============================================================
# SCARICA TUTTE LE PAGINE DEL CATALOGO
# ============================================================

print("=" * 50)
print("SCARICAMENTO CATALOGO COMPLETO VAVOO")
print("=" * 50)

vavoo = []
cursor = None
pagina = 0
ids_visti = set()

while True:
    params = {}

    if cursor is not None:
        params["cursor"] = cursor

    try:
        response = requests.get(
            VAVOO_CATALOG_URL,
            params=params,
            headers=VAVOO_HEADERS,
            timeout=30,
        )
        response.raise_for_status()
        catalog_data = response.json()

    except Exception as e:
        raise SystemExit(
            f"Errore durante il download della pagina {pagina + 1}: {e}"
        )

    if isinstance(catalog_data, list):
        items = catalog_data
        next_cursor = None

    elif isinstance(catalog_data, dict):
        items = (
            catalog_data.get("items", [])
            or catalog_data.get("channels", [])
            or catalog_data.get("data", [])
        )
        next_cursor = catalog_data.get("nextCursor")

    else:
        raise SystemExit("Formato del catalogo Vavoo non riconosciuto.")

    if not isinstance(items, list):
        raise SystemExit("La lista dei canali ricevuta non è valida.")

    pagina += 1
    aggiunti = 0

    for item in items:
        if not isinstance(item, dict):
            continue

        channel_id = str(item.get("id", "")).strip()
        channel_name = str(item.get("name", "")).strip()
        channel_url = str(item.get("url", "")).strip()
        print(json.dumps(item, ensure_ascii=False)[:1500])

        if not channel_id or not channel_name or not channel_url:
            continue

        if channel_id in ids_visti:
            continue

        ids_visti.add(channel_id)

        tags = item.get("tags", [])
        paese = tags[0] if tags else "Altro"

        vavoo.append({
            "name": channel_name,
            "id": channel_id,
            "url": channel_url,
            "country": paese,
        })

        aggiunti += 1

    print(
        f"Pagina {pagina}: ricevuti {len(items)}, "
        f"aggiunti {aggiunti}, totale {len(vavoo)}"
    )

    if next_cursor is None or next_cursor == "":
        break

    cursor = next_cursor


# ============================================================
# GENERA can.json SUDDIVISO PER PAESE
# ============================================================

canali_per_paese = {}

for channel in vavoo:
    # Recupera il paese dal campo tags del catalogo
    # (va aggiunto al salvataggio dei dati, vedi nota sotto)
    paese = channel.get("country", "Altro")

    canali_per_paese.setdefault(paese, []).append({
        "name": channel["name"],
        "id": channel["id"],
        "url": channel["url"],
    })

with open("can.json", "w", encoding="utf-8") as file:
    json.dump(canali_per_paese, file, ensure_ascii=False)

print("=" * 50)
print("CATALOGO VAVOO COMPLETATO")
print("Pagine scaricate:", pagina)
print("Canali salvati:", len(vavoo))
print("Paesi trovati:", len(canali_per_paese))
print("Creato can.json")
print("=" * 50)

