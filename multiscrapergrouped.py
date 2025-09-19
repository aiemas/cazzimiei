import requests
from bs4 import BeautifulSoup

session = requests.Session()

# Header comuni da usare ovunque
common_headers = {
    "User-Agent": "Mozilla/5.0 (SMART-TV; Linux; Tizen 6.0) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/2.1 TV Safari/537.36",
    "Referer": "https://jxoplay.xyz/",
    "Origin": "https://jxoplay.xyz",
    "Accept-Language": "en-US,en;q=0.5"
}

providers = {
    "nfs": "https://nfsnew.newkso.ru/nfs/",
    "wind": "https://windnew.newkso.ru/wind/",
    "x4": "https://x4new.newkso.ru/x4/",
    # aggiungi gli altri provider...
}

for name, provider in providers.items():
    print(f"🔎 Scansione provider: {provider} ({name})")
    try:
        # Scarica la pagina principale con header
        resp = session.get(provider, timeout=15, headers=common_headers)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        links = [a["href"] for a in soup.find_all("a", href=True) if "premium" in a["href"]]

        for link in links:
            full_folder = provider + link.strip("/")
            try:
                # Visita la sottocartella con header per "sbloccare" i link
                session.get(full_folder, timeout=7, headers=common_headers)
            except Exception as e:
                print(f"⚠️ Errore apertura sottocartella {full_folder}: {e}")
                continue

            # Qui costruisci il link .m3u8
            m3u8_url = full_folder + "/mono.m3u8"
            print(f"   ➕ Trovato: {m3u8_url}")

    except Exception as e:
        print(f"❌ Errore nel caricamento della pagina {provider}: {e}")
