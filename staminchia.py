import requests
from bs4 import BeautifulSoup
import json
import re

# ============================================================
# CONFIGURAZIONE
# ============================================================
URL = "https://dlstreams.st"
OUTPUT_JSON = "eventi.json"
OUTPUT_HTML = "index.html"  # Nome ideale per GitHub Pages

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    )
}

print("==========================================")
print("Scaricamento pagina...")
print("==========================================")

try:
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
except Exception as e:
    print("ERRORE durante il download:", e)
    exit()

html = response.text
soup = BeautifulSoup(html, "html.parser")
event_blocks = soup.select("div.schedule__event")
events = []

for event_block in event_blocks:
    time_element = event_block.select_one(".schedule__time")
    event_time = time_element.get_text(" ", strip=True) if time_element else ""

    title_element = event_block.select_one(".schedule__eventTitle")
    event_title = title_element.get_text(" ", strip=True) if title_element else ""

    channels = []
    channel_elements = event_block.select(".schedule__channels a")

    for channel_element in channel_elements:
        channel_name = channel_element.get_text(" ", strip=True)
        href = channel_element.get("href", "")
        match = re.search(r"[?&]id=(\d+)", href)

        if match:
            channel_id = match.group(1)
            # URL convertito nel formato embed richiesto
            final_url = f"https://dlhd.pk/embed/stream-{channel_id}.php"
        else:
            channel_id = ""
            final_url = ""

        channels.append({
            "name": channel_name,
            "id": channel_id,
            "watch_url": final_url
        })

    events.append({
        "time": event_time,
        "title": event_title,
        "channels": channels
    })

# Salva JSON locale
with open(OUTPUT_JSON, "w", encoding="utf-8") as file:
    json.dump(events, file, ensure_ascii=False, indent=4)

# ============================================================
# GENERAZIONE STRUTTURA HTML PER GITHUB
# ============================================================
html_content = """<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Palinsesto Eventi Live</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: var(--accent);
            margin-bottom: 30px;
        }
        .event-card {
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .event-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 14px;
            border-bottom: 1px solid #334155;
            padding-bottom: 8px;
        }
        .time {
            background-color: var(--accent);
            color: #0f172a;
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 0.9rem;
        }
        .title {
            font-size: 1.1rem;
            font-weight: 600;
        }
        .channels-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .btn-channel {
            background-color: #334155;
            color: var(--text-main);
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }
        .btn-channel:hover {
            background-color: var(--accent);
            color: #0f172a;
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📺 Palinsesto Eventi Live</h1>
"""

for event in events:
    if not event["channels"]:
        continue
    html_content += f'        <div class="event-card">\n'
    html_content += f'            <div class="event-header">\n'
    html_content += f'                <span class="time">{event["time"]}</span>\n'
    html_content += f'                <div class="title">{event["title"]}</div>\n'
    html_content += f'            </div>\n'
    html_content += f'            <div class="channels-list">\n'
    
    for ch in event["channels"]:
        if ch["watch_url"]:
            html_content += f'                <a class="btn-channel" href="{ch["watch_url"]}" target="_blank">🔗 {ch["name"]}</a>\n'
            
    html_content += f'            </div>\n'
    html_content += f'        </div>\n'

html_content += """    </div>
</body>
</html>"""

with open(OUTPUT_HTML, "w", encoding="utf-8") as html_file:
    html_file.write(html_content)

print("Processo completato!")
print(f"File aggiornati sul computer: {OUTPUT_JSON} e {OUTPUT_HTML}")
