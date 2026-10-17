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
