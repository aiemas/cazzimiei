import requests
from bs4 import BeautifulSoup
import json
import re


# ============================================================
# CONFIGURAZIONE
# ============================================================

URL = "https://dlstreams.st"
OUTPUT_FILE = "eventi.json"
OUTPUT_HTML = "index.html"  # Nome ideale per GitHub Pages


# ============================================================
# HEADERS
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    )
}


# ============================================================
# SCARICA LA PAGINA
# ============================================================

print("==========================================")
print("Scaricamento pagina...")
print("URL:", URL)
print("==========================================")

try:

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

except Exception as e:

    print()
    print("ERRORE durante il download:")
    print(e)
    exit()


html = response.text

print()
print("Pagina scaricata correttamente.")
print("Caratteri HTML:", len(html))


# ============================================================
# PARSING HTML
# ============================================================

soup = BeautifulSoup(
    html,
    "html.parser"
)


# ============================================================
# TROVA GLI EVENTI
# ============================================================

events = []

event_blocks = soup.select(
    "div.schedule__event"
)


print()
print("Eventi trovati:", len(event_blocks))
print()


# ============================================================
# ELABORA GLI EVENTI
# ============================================================

for event_block in event_blocks:

    # --------------------------------------------------------
    # ORARIO
    # --------------------------------------------------------

    time_element = event_block.select_one(
        ".schedule__time"
    )

    if time_element:

        event_time = time_element.get_text(
            " ",
            strip=True
        )

    else:

        event_time = ""


    # --------------------------------------------------------
    # NOME EVENTO
    # --------------------------------------------------------

    title_element = event_block.select_one(
        ".schedule__eventTitle"
    )

    if title_element:

        event_title = title_element.get_text(
            " ",
            strip=True
        )

    else:

        event_title = ""


    # --------------------------------------------------------
    # CANALI
    # --------------------------------------------------------

    channels = []


    channel_elements = event_block.select(
        ".schedule__channels a"
    )


    for channel_element in channel_elements:

        # ----------------------------------------------------
        # NOME CANALE
        # ----------------------------------------------------

        channel_name = channel_element.get_text(
            " ",
            strip=True
        )


        # ----------------------------------------------------
        # HREF
        # ----------------------------------------------------

        href = channel_element.get(
            "href",
            ""
        )


        # ----------------------------------------------------
        # ID
        # ----------------------------------------------------

        match = re.search(
            r"[?&]id=(\d+)",
            href
        )


        if match:

            channel_id = match.group(1)
            # COSTRUISCE IL NUOVO URL EMBED RICHIESTO
            final_url = f"https://dlhd.pk/embed/stream-{channel_id}.php"

        else:

            channel_id = ""
            final_url = ""


        # ----------------------------------------------------
        # AGGIUNGI CANALE
        # ----------------------------------------------------

        channels.append({

            "name": channel_name,

            "id": channel_id,

            "watch_url": final_url

        })


    # --------------------------------------------------------
    # SALVA EVENTO
    # --------------------------------------------------------

    events.append({

        "time": event_time,

        "title": event_title,

        "channels": channels

    })


# ============================================================
# SALVA JSON
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        events,
        file,
        ensure_ascii=False,
        indent=4
    )


# ============================================================
# GENERAZIONE STRUTTURA HTML CON BARRA E PLAYER INTEGRATO
# ============================================================

html_content = """<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IPTV Dashboard</title>
    <style>
        :root {
            --bg: #0b0f19; --sidebar: #131a2c; --card: #1e293b;
            --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background: var(--bg); color: var(--text);
            display: flex; height: 100vh; overflow: hidden;
        }
        .sidebar {
            width: 360px; background: var(--sidebar);
            border-right: 1px solid #223049; display: flex; flex-direction: column;
        }
        .sidebar-header { padding: 15px; border-bottom: 1px solid #223049; }
        .sidebar-header h1 { font-size: 1.2rem; color: var(--accent); margin-bottom: 10px; }
        .search-box {
            width: 100%; padding: 8px 12px; background: #1e293b;
            border: 1px solid #334155; border-radius: 6px; color: #fff; outline: none;
        }
        .events-list { flex: 1; overflow-y: auto; padding: 10px; }
        .event-card {
            background: var(--card); border-radius: 6px; padding: 10px;
            margin-bottom: 8px; cursor: pointer; border: 1px solid transparent;
        }
        .event-card:hover { border-color: #334155; }
        .time {
            background: var(--accent); color: #0b0f19; padding: 2px 5px;
            border-radius: 4px; font-weight: bold; font-size: 0.75rem; display: inline-block; margin-bottom: 4px;
        }
        .title { font-size: 0.9rem; font-weight: 600; }
        .channels-wrapper {
            margin-top: 8px; display: none; padding-top: 6px; border-top: 1px solid #334155; flex-direction: column; gap: 4px;
        }
        .event-card.active .channels-wrapper { display: flex; }
        .btn-channel {
            background: #334155; color: #fff; padding: 6px 10px; border-radius: 4px;
            font-size: 0.8rem; text-align: left; border: none; cursor: pointer; width: 100%;
        }
        .btn-channel:hover { background: var(--accent); color: #0b0f19; }
        .main-content { flex: 1; display: flex; flex-direction: column; background: #000; }
        .player-header { background: var(--sidebar); padding: 12px 15px; border-bottom: 1px solid #223049; font-weight: bold; }
        .player-container { flex: 1; position: relative; width: 100%; height: 100%; }
        iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none; background: #000; }
        .no-video {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            text-align: center; color: var(--muted); font-size: 1rem; width: 90%; pointer-events: none;
        }
        @media (max-width: 768px) {
            body { flex-direction: column-reverse; }
            .sidebar { width: 100%; height: 40vh; } .main-content { height: 60vh; }
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-header">
            <h1>📺 Palinsesto Live</h1>
            <input type="text" id="search" class="search-box" placeholder="Cerca evento...">
        </div>
        <div class="events-list">
"""

for event in events:
    if not event["channels"]:
        continue
    valid_ch = [c for c in event["channels"] if c["watch_url"]]
    if not valid_ch:
        continue

    html_content += f'            <div class="event-card" onclick="toggleCard(this)">\n'
    html_content += f'                <div><span class="time">{event["time"]}</span></div>\n'
    html_content += f'                <div class="title">{event["title"]}</div>\n'
    html_content += f'                <div class="channels-wrapper">\n'
    
        for ch in valid_ch:
        t_clean = event["title"].replace("'", " ").replace('"', ' ')
        c_clean = ch["name"].replace("'", " ").replace('"', ' ')
        # Raddrizzato l'uso degli apici esterni per evitare i conflitti con il backslash
        html_content += """                    <button class="btn-channel" onclick="loadStream('""" + ch["watch_url"] + """', '""" + t_clean + " - " + c_clean + """', event)">🔗 """ + ch["name"] + """</button>\n"""
            
    html_content += f'                </div>\n'
    html_content += f'            </div>\n'

html_content += """        </div>
    </div>
    <div class="main-content">
        <div class="player-header" id="p-title">Nessun canale selezionato</div>
        <div class="player-container">
            <div class="no-video" id="placeholder">Scegli un evento e clicca su un canale per avviare il riproduttore</div>
            <iframe id="live-player" src="" allowfullscreen allow="autoplay; encrypted-media"></iframe>
        </div>
    </div>
    <script>
        function toggleCard(card) {
            const wasActive = card.classList.contains('active');
            document.querySelectorAll('.event-card').forEach(c => c.classList.remove('active'));
            if (!wasActive) card.classList.add('active');
        }
                function loadStream(url, title) {
            // Riferimenti corretti per lo svuotamento del placeholder e iniezione URL
            document.getElementById('placeholder').style.display = 'none';
            document.getElementById('live-player').src = url;
            document.getElementById('p-title').textContent = "🟢 In onda: " + title;
        }

        document.getElementById('search').addEventListener('input', function(e) {
            const q = e.target.value.toLowerCase();
            document.querySelectorAll('.event-card').forEach(card => {
                card.style.display = card.textContent.toLowerCase().includes(q) ? 'block' : 'none';
            });
        });
    </script>
</body>
</html>"""

with open(OUTPUT_HTML, "w", encoding="utf-8") as html_file:
    html_file.write(html_content)



# ============================================================
# STAMPA RISULTATO
# ============================================================

print("==========================================")
print("RISULTATO")
print("==========================================")
print()


for event in events:

    print(
        f'[{event["time"]}] {event["title"]}'
    )


    for channel in event["channels"]:

        print(
            f'    - {channel["name"]}'
            f' | URL: {channel["watch_url"]}'
        )


    print()


print("==========================================")
print("FINE")
print("==========================================")

print()
print("File creati correttamente:")
print(f"- {OUTPUT_FILE}")
print(f"- {OUTPUT_HTML}")
