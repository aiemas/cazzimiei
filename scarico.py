import requests
import json
import os
import time
from pathlib import Path


# ============================================================
# CONFIGURAZIONE
# ============================================================

URL = "https://vixsrc.to/api/list/movie/?lang=it"
URL_TV = "https://vixsrc.to/api/list/tv/?lang=it"

OUTPUT_LISTONE = "listone.json"
OUTPUT_LISTONE_TV = "listone_tv.json"

OUTPUT_VOD = "vod.json"
OUTPUT_TV = "tv.json"

TMDB_API_URL = "https://api.themoviedb.org/3/movie"
TMDB_TV_API_URL = "https://api.themoviedb.org/3/tv"


# ============================================================
# SCARICA LISTA VIX
# ============================================================

def scarica_listone():

    print(f"Scarico: {URL}")

    response = requests.get(
        URL,
        timeout=60,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    print(f"HTTP: {response.status_code}")
    print(f"Dimensione risposta: {len(response.content)} byte")

    data = response.json()

    Path(OUTPUT_LISTONE).write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print(f"Creato: {OUTPUT_LISTONE}")

    return data

def scarica_listone_tv():

    print(f"Scarico: {URL_TV}")

    response = requests.get(
        URL_TV,
        timeout=60,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    print(f"HTTP: {response.status_code}")
    print(f"Dimensione risposta: {len(response.content)} byte")

    data = response.json()

    Path(OUTPUT_LISTONE_TV).write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print(f"Creato: {OUTPUT_LISTONE_TV}")

    return data


# ============================================================
# CREA / AGGIORNA VOD.JSON
# ============================================================

def crea_vod(data):

    api_key = os.environ.get("TMDB_API_KEY")

    if not api_key:
        raise RuntimeError(
            "TMDB_API_KEY non trovata nelle variabili d'ambiente"
        )

    # --------------------------------------------------------
    # Carica vod.json esistente, se presente
    # --------------------------------------------------------

    percorso_vod = Path(OUTPUT_VOD)

    if percorso_vod.exists():

        print()
        print(f"Carico {OUTPUT_VOD} esistente...")

        try:
            film = json.loads(
                percorso_vod.read_text(
                    encoding="utf-8"
                )
            )

            if not isinstance(film, list):
                print("vod.json non contiene una lista. Lo ricreo.")
                film = []

        except Exception as errore:

            print(
                f"Errore nella lettura di {OUTPUT_VOD}: {errore}"
            )

            film = []

    else:

        print()
        print(
            f"{OUTPUT_VOD} non esiste. "
            "Verrà creato da zero."
        )

        film = []

    # --------------------------------------------------------
    # Crea indice degli ID già presenti
    # --------------------------------------------------------

    ids_esistenti = {
        elemento.get("tmdb_id")
        for elemento in film
        if elemento.get("tmdb_id")
    }

    # --------------------------------------------------------
    # Trova solamente i nuovi film
    # --------------------------------------------------------

    nuovi_film = []

    for elemento in data:

        tmdb_id = elemento.get("tmdb_id")

        if not tmdb_id:
            continue

        if tmdb_id not in ids_esistenti:
            nuovi_film.append(elemento)

    print()
    print(f"Film presenti in listone Vix: {len(data)}")
    print(f"Film già presenti in vod.json: {len(ids_esistenti)}")
    print(f"Nuovi film da scaricare: {len(nuovi_film)}")
    print()

    # --------------------------------------------------------
    # Se non ci sono nuovi film, non interroga TMDB
    # --------------------------------------------------------

    if not nuovi_film:

        print("Nessun nuovo film.")
        print("vod.json rimane invariato.")

        return

    # --------------------------------------------------------
    # Scarica da TMDB solamente i nuovi film
    # --------------------------------------------------------

    print("Inizio recupero dati TMDB per i nuovi film...")
    print()

    totale_nuovi = len(nuovi_film)

    for indice, elemento in enumerate(nuovi_film, start=1):

        tmdb_id = elemento.get("tmdb_id")
        imdb_id = elemento.get("imdb_id")

        print(
            f"[{indice}/{totale_nuovi}] "
            f"TMDB ID: {tmdb_id}"
        )

        try:

            response = requests.get(
                f"{TMDB_API_URL}/{tmdb_id}",
                params={
                    "api_key": api_key,
                    "language": "it-IT"
                },
                timeout=30,
                headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )

            if response.status_code == 404:

                print(
                    f"    Film non trovato su TMDB: {tmdb_id}"
                )

                continue

            response.raise_for_status()

            dati = response.json()

            film.append({
                "tmdb_id": tmdb_id,
                "imdb_id": imdb_id,
                "title": dati.get("title"),
                "original_title": dati.get("original_title"),
                "year": (
                    dati.get("release_date", "")[:4]
                    if dati.get("release_date")
                    else None
                ),
                "poster": (
                    f"https://image.tmdb.org/t/p/w500"
                    f"{dati['poster_path']}"
                    if dati.get("poster_path")
                    else None
                ),
                "backdrop": (
                    f"https://image.tmdb.org/t/p/w1280"
                    f"{dati['backdrop_path']}"
                    if dati.get("backdrop_path")
                    else None
                ),
                "rating": dati.get("vote_average"),
                "overview": dati.get("overview"),
                "genres": [
                    genere.get("name")
                    for genere in dati.get("genres", [])
                ]
            })

            print(
                f"    OK: {dati.get('title')}"
            )

        except Exception as errore:

            print(
                f"    ERRORE TMDB {tmdb_id}: {errore}"
            )

        time.sleep(0.1)

    # --------------------------------------------------------
    # Salva vod.json aggiornato
    # --------------------------------------------------------

    percorso_vod.write_text(
        json.dumps(
            film,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print()
    print(
        f"Aggiornato {OUTPUT_VOD} "
        f"con {len(film)} film totali."
    )

# ============================================================
# CREA / AGGIORNA TV.JSON
# ============================================================

def crea_tv(data):

    api_key = os.environ.get("TMDB_API_KEY")

    if not api_key:
        raise RuntimeError(
            "TMDB_API_KEY non trovata nelle variabili d'ambiente"
        )

    # --------------------------------------------------------
    # Carica tv.json esistente, se presente
    # --------------------------------------------------------

    percorso_tv = Path(OUTPUT_TV)

    if percorso_tv.exists():

        print()
        print(f"Carico {OUTPUT_TV} esistente...")

        try:
            serie = json.loads(
                percorso_tv.read_text(
                    encoding="utf-8"
                )
            )

            if not isinstance(serie, list):
                print("tv.json non contiene una lista. Lo ricreo.")
                serie = []

        except Exception as errore:

            print(
                f"Errore nella lettura di {OUTPUT_TV}: {errore}"
            )

            serie = []

    else:

        print()
        print(
            f"{OUTPUT_TV} non esiste. "
            "Verrà creato da zero."
        )

        serie = []

    # --------------------------------------------------------
    # Crea indice degli ID già presenti
    # --------------------------------------------------------

    ids_esistenti = {
        elemento.get("tmdb_id")
        for elemento in serie
        if elemento.get("tmdb_id")
    }

    # --------------------------------------------------------
    # Trova solamente le nuove serie
    # --------------------------------------------------------

    nuove_serie = []

    for elemento in data:

        tmdb_id = elemento.get("tmdb_id")

        if not tmdb_id:
            continue

        if tmdb_id not in ids_esistenti:
            nuove_serie.append(elemento)

    print()
    print(f"Serie presenti in listone TV Vix: {len(data)}")
    print(f"Serie già presenti in tv.json: {len(ids_esistenti)}")
    print(f"Nuove serie da scaricare: {len(nuove_serie)}")
    print()

    # --------------------------------------------------------
    # Se non ci sono nuove serie, non interroga TMDB
    # --------------------------------------------------------

    if not nuove_serie:

        print("Nessuna nuova serie.")
        print("tv.json rimane invariato.")

        return

    # --------------------------------------------------------
    # Scarica da TMDB solamente le nuove serie
    # --------------------------------------------------------

    print("Inizio recupero dati TMDB per le nuove serie...")
    print()

    totale_nuove = len(nuove_serie)

    for indice, elemento in enumerate(nuove_serie, start=1):

        tmdb_id = elemento.get("tmdb_id")
        imdb_id = elemento.get("imdb_id")

        print(
            f"[{indice}/{totale_nuove}] "
            f"TMDB ID: {tmdb_id}"
        )

        try:

            response = requests.get(
                f"{TMDB_TV_API_URL}/{tmdb_id}",
                params={
                    "api_key": api_key,
                    "language": "it-IT"
                },
                timeout=30,
                headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )

            if response.status_code == 404:

                print(
                    f"    Serie non trovata su TMDB: {tmdb_id}"
                )

                continue

            response.raise_for_status()

            dati = response.json()

            stagioni = []

            for stagione in dati.get("seasons", []):

                numero_stagione = stagione.get(
                    "season_number"
                )

                numero_episodi = stagione.get(
                    "episode_count"
                )

                if numero_stagione is None:
                    continue

                stagioni.append({
                    "season": numero_stagione,
                    "episodes": numero_episodi or 0
                })

            serie.append({
                "tmdb_id": tmdb_id,
                "imdb_id": imdb_id,
                "type": "tv",
                "title": dati.get("name"),
                "original_title": dati.get("original_name"),
                "year": (
                    dati.get("first_air_date", "")[:4]
                    if dati.get("first_air_date")
                    else None
                ),
                "poster": (
                    f"https://image.tmdb.org/t/p/w500"
                    f"{dati['poster_path']}"
                    if dati.get("poster_path")
                    else None
                ),
                "backdrop": (
                    f"https://image.tmdb.org/t/p/w1280"
                    f"{dati['backdrop_path']}"
                    if dati.get("backdrop_path")
                    else None
                ),
                "rating": dati.get("vote_average"),
                "overview": dati.get("overview"),
                "genres": [
                    genere.get("name")
                    for genere in dati.get("genres", [])
                ],
                "seasons": stagioni
            })

            print(
                f"    OK: {dati.get('name')} "
                f"({len(stagioni)} stagioni)"
            )

        except Exception as errore:

            print(
                f"    ERRORE TMDB {tmdb_id}: {errore}"
            )

        time.sleep(0.1)

    # --------------------------------------------------------
    # Salva tv.json aggiornato
    # --------------------------------------------------------

    percorso_tv.write_text(
        json.dumps(
            serie,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print()
    print(
        f"Aggiornato {OUTPUT_TV} "
        f"con {len(serie)} serie totali."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    data = scarica_listone()
    data_tv = scarica_listone_tv()

    crea_vod(data)
    crea_tv(data_tv)


if __name__ == "__main__":
    main()
