import requests
from bs4 import BeautifulSoup
import time
import random

providers = [
    "https://esx1new.newkso.ru/esx1/",
    "https://x4-cdnnew.newkso.ru/x4-cdn/",
    "https://top2new.newkso.ru/top2/",
    "https://windnew.newkso.ru/wind/",
    "https://x4new.newkso.ru/x4/",
    "https://wikinew.newkso.ru/wiki/",
    "https://dokko1new.newkso.ru/dokko1/",
    "https://azonew.newkso.ru/azo/",
    "https://wikihznew.newkso.ru/wikihz/",
    "https://nfsnew.newkso.ru/nfs/",
    "https://ddy6new.newkso.ru/ddy6/",
    "https://zekonew.newkso.ru/zeko/",
    "https://calcio.newkso.ru/calcio/",
    "https://top2-cdn.newkso.ru/top2-cdn/",
    "https://top1-cdnnew.newkso.ru/top1-cdn/",
    "https://hztnew.newkso.ru/hzt/",
    "https://top1.newkso.ru/top1/",
    "https://max2new.newkso.ru/max2/",
]

referer = "https://jxoplay.xyz/"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"


session = requests.Session()
session.headers.update({
    "User-Agent": user_agent,
    "Referer": referer,
    "Accept-Language": "en-US,en;q=0.5"
})

channels_by_provider = {}

for provider in providers:
    provider_key = provider.strip("/").split("/")[-1]  # es: nfsnew, windnew
    print(f"\n🔎 Scansione provider: {provider} ({provider_key})")
    channels_by_provider[provider_key] = []

    try:
        resp = session.get(provider, timeout=180)
        resp.raise_for_status()
    except Exception as e:
        print(f"❌ Errore nel caricamento della pagina {provider}: {e}")
        continue

    soup = BeautifulSoup(resp.text, "html.parser")
    channel_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.endswith("/") and href != "../":
            full_link = provider + href
            channel_links.append(full_link)

    print(f"  ➔ Trovati {len(channel_links)} canali/sottocartelle")

    for channel in channel_links:
        try:
            page = session.get(channel, timeout=5)
            page.raise_for_status()
        except Exception as e:
            print(f"    ⚠️  Errore nel caricamento {channel}: {e}")
            continue

        page_soup = BeautifulSoup(page.text, "html.parser")
        found = False

        for a in page_soup.find_all("a", href=True):
            if ".m3u8" in a["href"]:
                m3u8_link = a["href"]
                if not m3u8_link.startswith("http"):
                    m3u8_link = channel + m3u8_link

                try:
                    head_resp = session.head(m3u8_link, timeout=5)
                    if head_resp.status_code == 200:
                        parts = channel.strip("/").split("/")
                        channel_name = parts[-1] if parts else "Unknown"
                        channels_by_provider[provider_key].append((channel_name, m3u8_link))
                        print(f"    ✅ Valido: {channel_name} → {m3u8_link}")
                    else:
                        print(f"    ❌ Link offline ({head_resp.status_code}): {m3u8_link}")
                except Exception as e:
                    print(f"    ❌ Errore nel controllo link {m3u8_link}: {e}")
                found = True

        if not found:
            print(f"    ⚠️ Nessun link .m3u8 trovato in {channel}")


# Scrivi la playlist raggruppata con veri gruppi group-title
with open("multigroup.m3u", "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    total = 0
    for provider, channels in channels_by_provider.items():
        if channels:
            print(f"\n📁 Scrittura gruppo {provider.upper()} con {len(channels)} canali")
            for channel_name, url in channels:
                f.write(f'#EXTINF:-1 group-title="{provider.upper()}",{channel_name}\n')
                f.write(f"#EXTVLCOPT:http-referrer={referer}\n")  # Aggiunta dell'intestazione Referer
                f.write(f"#EXTVLCOPT:user-agent={user_agent}\n")  # Aggiunta dell'intestazione User-Agent
                f.write(f"{url}\n")
                total += 1

if total:
    print(f"\n🎉 Playlist salvata come multigroup.m3u con {total} canali raggruppati in veri gruppi per provider!")
else:
    print("\n⚠️ Nessun link valido trovato. Playlist non creata.")