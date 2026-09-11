import requests
import json
from pathlib import Path


URL = "https://vixsrc.to/api/list/movie/?lang=it"
OUTPUT_FILE = "listone.json"


def main():

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

    # Verifichiamo che la risposta sia effettivamente JSON
    data = response.json()

    # Salviamo il contenuto così come viene restituito dall'API
    Path(OUTPUT_FILE).write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print(f"Creato: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
