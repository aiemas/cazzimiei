
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

print("=" * 60)
print("SCARICAMENTO CATALOGO VAVOO COMPLETO")
print("=" * 60)

vavoo_items = []
cursor = None
pagina = 1
cursori_usati = set()

while True:
    params = {"cursor": cursor} if cursor is not None else {}

    try:
        response = requests.get(
            VAVOO_CATALOG_URL,
            headers=VAVOO_HEADERS,
            params=params,
            timeout=30
        )
        response.raise_for_status()
        catalog_data = response.json()

    except Exception as e:
        raise SystemExit(
            f"Errore nella pagina {pagina}, cursor={cursor}: {e}"
        )

    if isinstance(catalog_data, list):
        items = catalog_data
        next_cursor = None

    elif isinstance(catalog_data, dict):
        items = (
            catalog_data.get("items", [])
            or catalog_data.get("channels", [])
        )

        if not items and isinstance(catalog_data.get("data"), list):
            items = catalog_data["data"]

        next_cursor = catalog_data.get("nextCursor")

    else:
        raise SystemExit(
            f"Formato risposta non valido nella pagina {pagina}"
        )

    if not isinstance(items, list):
        raise SystemExit(
            f"Elenco canali non valido nella pagina {pagina}"
        )

    print(f"\nPagina: {pagina}")
    print("URL:", response.url)
    print("Elementi ricevuti:", len(items))
    print("nextCursor:", next_cursor)

    if items:
        print("Primo canale:", items[0].get("name", ""))
        print("Ultimo canale:", items[-1].get("name", ""))

    vavoo_items.extend(items)

    if next_cursor is None or next_cursor == "":
        print("\nFine del catalogo: nessun altro cursore.")
        break

    cursor_key = str(next_cursor)

    if cursor_key in cursori_usati:
        raise SystemExit(
            f"Interruzione: cursore ripetuto ({cursor_key})."
        )

    cursori_usati.add(cursor_key)
    cursor = next_cursor
    pagina += 1

# ============================================================
# RIEPILOGO
# ============================================================

print("\n" + "=" * 60)
print("CATALOGO VAVOO SCARICATO")
print("Pagine ricevute:", pagina)
print("Totale elementi ricevuti:", len(vavoo_items))
print("=" * 60)

print("\nPRIMI 10 CANALI:")

for numero, item in enumerate(vavoo_items[:10], start=1):
    if not isinstance(item, dict):
        continue

    print(
        f"{numero}. "
        f"NOME: {item.get('name', '')} | "
        f"ID: {item.get('id', '')} | "
        f"URL: {item.get('url', '')}"
    )
