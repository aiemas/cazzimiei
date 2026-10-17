import json
import re
import requests

# ============================================================
# CONFIGURAZIONE VAVOO
# ============================================================

VAVOO_CATALOG_URL = "https://vavoo.to/live/catalog/live/channels.json?region=IT&language=it&sort=trending&filter%5Bgroup%5D=Italy"
VAVOO_RESOLVE_URL = "https://vavoo.to/live/resolve"

VAVOO_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, */*",
    "Accept-Language": "it",
    "Referer": "https://vavoo.to/",
}

VAVOO_CANALI_DESIDERATI = {

    "SKY CINEMA ACTION",
    "SKY CINEMA COLLECTION",
    "SKY CINEMA COMEDY",
    "SKY CINEMA DRAMA",
    "SKY CINEMA DUE",
    "SKY CINEMA FAMILY",
    "SKY CINEMA ROMANCE",
    "SKY CINEMA SUSPENSE",
    "SKY CINEMA UNO",

    "SKY UNO",
    "SKY ARTE",
    "SKY ATLANTIC",
    "SKY SERIE",
    "SKY INVESTIGATION",
    "SKY CRIME",
    "SKY DOCUMENTARIES",

    "HISTORY",
    "COMEDY CENTRAL",

    "SKY SPORT UNO",
    "SKY SPORT TENNIS",
    "SKY SPORT 24",
    "SKY SPORT ARENA",
    "SKY SPORT CALCIO",
    "SKY SPORT F1",
    "SKY SPORT MOTOGP",
    "SKY SPORT MAX",
    "SKY SPORT BASKET",

    "CARTOON NETWORK",
    "NICK JR",
    "NICKELODEON",
    "BOOMERANG",

    "SKY PRIMAFILA 1",
    "SKY PRIMAFILA 2",
    "SKY PRIMAFILA 3",
    "SKY PRIMAFILA 4",
    "SKY PRIMAFILA 5",
    "SKY PRIMAFILA 6",
    "SKY PRIMAFILA 7",
    "SKY PRIMAFILA 8",
    "SKY PRIMAFILA 9",
    "SKY PRIMAFILA 10",
    "SKY PRIMAFILA 11",
    "SKY PRIMAFILA 12",
    "SKY PRIMAFILA 13",
    "SKY PRIMAFILA 14",
    "SKY PRIMAFILA 15",
    "SKY PRIMAFILA 16",
    "SKY PRIMAFILA 18",

    "SKY PRIMAFILA PREMIERE 01",
    "SKY PRIMAFILA PREMIERE 02"
}

def normalizza_nome_vavoo(nome):

    nome = str(nome).strip()

    # Rimuove i suffissi utilizzati da VAVOO
    nome = re.sub(
        r"\s*\.(c|s)\s*$",
        "",
        nome,
        flags=re.IGNORECASE
    )

    # Rimuove E/H utilizzati nella M3U
    nome = re.sub(
        r"\s*\|[EH]\s*$",
        "",
        nome,
        flags=re.IGNORECASE
    )

    # Rimuove diciture BACKUP
    nome = re.sub(
        r"\s*\(BACKUP\)\s*$",
        "",
        nome,
        flags=re.IGNORECASE
    )

    # Rimuove spazi multipli
    nome = re.sub(
        r"\s+",
        " ",
        nome
    )

    return nome.strip().upper()

VAVOO_CANALI_DESIDERATI_NORMALIZZATI = {
    normalizza_nome_vavoo(nome) for nome in VAVOO_CANALI_DESIDERATI
}

VAVOO_LOGHI = {
    "SKY CINEMA ACTION": "https://pixel.disco.nowtv.it/logo/skychb_206_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY CINEMA COLLECTION": "https://pixel.disco.nowtv.it/logo/skychb_204_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY CINEMA COMEDY": "https://pixel.disco.nowtv.it/logo/skychb_30_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY CINEMA DRAMA": "https://pixel.disco.nowtv.it/logo/skychb_769_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY CINEMA DUE": "https://pixel.disco.nowtv.it/logo/skychb_564_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY CINEMA FAMILY": "https://pixel.disco.nowtv.it/logo/skychb_255_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY CINEMA ROMANCE": "https://pixel.disco.nowtv.it/logo/skychb_231_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY CINEMA SUSPENSE": "https://pixel.disco.nowtv.it/logo/skychb_47_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY CINEMA UNO": "https://pixel.disco.nowtv.it/logo/skychb_202_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",

    "SKY UNO": "https://pixel.disco.nowtv.it/logo/skychb_477_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY ARTE": "https://pixel.disco.nowtv.it/logo/skychb_74_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY ATLANTIC": "https://pixel.disco.nowtv.it/logo/skychb_226_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY SERIE": "https://pixel.disco.nowtv.it/logo/skychb_684_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY INVESTIGATION": "https://pixel.disco.nowtv.it/logo/skychb_686_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY CRIME": "https://pixel.disco.nowtv.it/logo/skychb_249_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY DOCUMENTARIES": "https://pixel.disco.nowtv.it/logo/skychb_226_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "HISTORY": "https://pixel.disco.nowtv.it/logo/skychb_513_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "COMEDY CENTRAL": "https://pixel.disco.nowtv.it/logo/skychb_404_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",

    "SKY SPORT UNO": "https://pixel.disco.nowtv.it/logo/skychb_23_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY SPORT TENNIS": "https://pixel.disco.nowtv.it/logo/skychb_559_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY SPORT 24": "https://pixel.disco.nowtv.it/logo/skychb_35_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY SPORT ARENA": "https://pixel.disco.nowtv.it/logo/skychb_24_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY SPORT CALCIO": "https://pixel.disco.nowtv.it/logo/skychb_209_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY SPORT F1": "https://pixel.disco.nowtv.it/logo/skychb_478_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY SPORT MOTOGP": "https://pixel.disco.nowtv.it/logo/skychb_483_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY SPORT MAX": "https://pixel.disco.nowtv.it/logo/skychb_248_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "SKY SPORT BASKET": "https://pixel.disco.nowtv.it/logo/skychb_764_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",

    "CARTOON NETWORK": "https://pixel.disco.nowtv.it/logo/skychb_258_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "NICK JR": "https://pixel.disco.nowtv.it/logo/skychb_424_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "NICKELODEON": "https://pixel.disco.nowtv.it/logo/skychb_320_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",
    "BOOMERANG": "https://pixel.disco.nowtv.it/logo/skychb_367_darknow/LOGO_CHANNEL_LIGHT/4000?language=it-IT&proposition=NOWOTT",

    # Tutti i canali Sky Primafila usano lo stesso logo
    "SKY PRIMAFILA 1": "https://iconape.com/wp-content/files/ry/282239/png/sky-primafila-logo.png",
    "SKY PRIMAFILA 2": "https://iconape.com/wp-content/files/ry/282239/png/sky-primafila-logo.png",
    "SKY PRIMAFILA 3": "https://iconape.com/wp-content/files/ry/282239/png/sky-primafila-logo.png",
    "SKY PRIMAFILA 4": "https://iconape.com/wp-content/files/ry/282239/png/sky-primafila-logo.png",
    "SKY PRIMAFILA 5": "https://iconape.com/wp-content/files/ry/282239/png/sky-primafila-logo.png",
    "SKY PRIMAFILA 6": "https://iconape.com/wp-content/files/ry/282239/png/sky-primafila-logo.png",
    "SKY PRIMAFILA 7": "https://iconape.com/wp-content/files/ry/282239/png/sky-primafila-logo.png",
    "SKY PRIMAFILA 8": "https://iconape.com/wp-content/files/ry/282239/png/sky-primafila-logo.png",
    "SKY PRIMAFILA 9": "https://iconape.com/wp-content/files/ry/282239/png/sky-primafila-logo.png",
    "SKY PRIMAFILA 10": "https://iconape.com/wp-content/files/ry/282239/png/sky-primafila-logo.png",
    "SKY PRIMAFILA 11": "https://iconape.com/wp-content/files/ry/282239/png/sky-primafila-logo.png",
    "SKY PRIMAFILA 12": "https://iconape.com/wp-content/files/ry/282239/png/sky-primafila-logo.png",
    "SKY PRIMAFILA 13": "https://iconape.com/wp-content/files/ry/282239/png/sky-primafila-logo.png",
    "SKY PRIMAFILA 14": "https://iconape.com/wp-content/files/ry/282239/png/sky-primafila-logo.png",
    "SKY PRIMAFILA 15": "https://iconape.com/wp-content/files/ry/282239/png/sky-primafila-logo.png",
    "SKY PRIMAFILA 16": "https://iconape.com/wp-content/files/ry/282239/png/sky-primafila-logo.png",
    "SKY PRIMAFILA 18": "https://iconape.com/wp-content/files/ry/282239/png/sky-primafila-logo.png",
    "SKY PRIMAFILA PREMIERE 01": "https://iconape.com/wp-content/files/ry/282239/png/sky-primafila-logo.png",
    "SKY PRIMAFILA PREMIERE 02": "https://iconape.com/wp-content/files/ry/282239/png/sky-primafila-logo.png",
}

# ============================================================
# SCARICA CATALOGO VAVOO
# ============================================================

print("=" * 50)
print("SCARICAMENTO CATALOGO VAVOO ITALIA")
print("=" * 50)

try:
    response = requests.get(VAVOO_CATALOG_URL, headers=VAVOO_HEADERS, timeout=30)
    response.raise_for_status()
    catalog_data = response.json()
except Exception as e:
    raise SystemExit(f"Errore durante il download del catalogo VAVOO: {e}")

if isinstance(catalog_data, list):
    vavoo_items = catalog_data
elif isinstance(catalog_data, dict):
    vavoo_items = catalog_data.get("items", []) or catalog_data.get("channels", [])
    if not vavoo_items and isinstance(catalog_data.get("data"), list):
        vavoo_items = catalog_data["data"]
else:
    vavoo_items = []

print("Canali ricevuti dal catalogo:", len(vavoo_items))
print("\n=== NOMI REALI RESTITUITI DA VAVOO ===")
for item in vavoo_items[:50]:
    print(
        "name =", repr(item.get("name")),
        "| id =", repr(item.get("id")),
        "| url =", repr(item.get("url"))
    )
print("=== FINE NOMI CATALOGO ===\n")

# ============================================================
# FILTRA E PREPARA SOLO I CANALI DESIDERATI
# ============================================================

vavoo = []
nomi_trovati = set()

for item in vavoo_items:
    channel_id = str(item.get("id", "")).strip()
    channel_name = str(item.get("name", "")).strip()
    nome_normalizzato = normalizza_nome_vavoo(channel_name)

    # Non risolviamo canali che non sono nella lista scelta.
    if not channel_id or not channel_name or nome_normalizzato not in VAVOO_CANALI_DESIDERATI_NORMALIZZATI:
        continue

    nomi_trovati.add(nome_normalizzato)

    try:
        resolve_response = requests.get(
            VAVOO_RESOLVE_URL,
            params={
                "region": "IT",
                "language": "it",
                "url": item.get("url", ""),
            },
            headers=VAVOO_HEADERS,
            timeout=20,
        )
        resolve_response.raise_for_status()
        resolve_data = resolve_response.json()
        watch_url = resolve_data.get("url", "")

        if not watch_url:
            raise ValueError("URL streaming assente nella risposta")

        images = item.get("images", {}) or {}
        logo_vavoo = images.get("logo", "")
        if logo_vavoo and logo_vavoo.startswith("/"):
            logo_vavoo = "https://vavoo.to" + logo_vavoo

        logo_finale = logo_vavoo or VAVOO_LOGHI.get(nome_normalizzato, "")

        vavoo.append({
            "name": channel_name,
            "id": channel_id,
            "watch_url": watch_url,
            "logo": logo_finale,
        })
        print(f"[OK] {channel_name}")

    except Exception as e:
        print(f"[ERRORE RESOLVE] {channel_name} (ID: {channel_id}): {e}")

# ============================================================
# GENERA can.json
# ============================================================

with open("can.json", "w", encoding="utf-8") as file:
    json.dump(vavoo, file, ensure_ascii=False)
print(f"\n[OK] Creato can.json con {len(vavoo)} canali.")

# ============================================================
# GENERA can.m3u
# ============================================================

with open("can.m3u", "w", encoding="utf-8") as file:
    file.write("#EXTM3U\n")
    for channel in vavoo:
        name = channel.get("name", "")
        url = channel.get("watch_url", "")
        logo = channel.get("logo", "")
        channel_id = channel.get("id", "")
        if not url:
            continue
        file.write(
            f'#EXTINF:-1 tvg-id="{channel_id}" tvg-name="{name}" tvg-logo="{logo}",{name}\n'
        )
        file.write(f"{url}\n")

print(f"[OK] Creato can.m3u con {len(vavoo)} canali.")
print("=" * 50)
print("CATALOGO VAVOO COMPLETATO")
print("Canali selezionati e risolti:", len(vavoo))
print("=" * 50)
