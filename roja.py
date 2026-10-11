from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import time

url = "http://rojadirecta.eu"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("window-size=1200x800")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
chrome_options.add_argument("--disable-features=HttpsUpgrades")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--ignore-ssl-errors")
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

print(f"Estrazione TOTALE degli eventi e generazione lista IPTV ANNIDATA (Lingua Singola) da: {url}...")

m3u_path = "palinsesto.m3u"

try:
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    
    # Attendiamo il caricamento completo della pagina
    time.sleep(6)
    
    html_source = driver.page_source
    driver.quit()
    
    soup = BeautifulSoup(html_source, 'html.parser')
    
    m3u_lines = ["#EXTM3U"]
    
    current_event = None
    event_streams = []

    sports_keywords = ['Calcio', 'Tennis', 'Rugby', 'Golf', 'Fútbol', 'Automovilismo', 'Motor Sport', 'F1', 'MotoGP', 'Superbike', 'WorldSBK']

    # Analizziamo in modo lineare e inclusivo ogni blocco tr o div della pagina
    for el in soup.find_all(['div', 'span', 'tr', 'li']):
        text = el.get_text(separator=" ", strip=True)
        
        # Un evento valido su Rojadirecta inizia sempre con un orario (es. 12:30, 10:45)
        if text and len(text) > 15 and text[0:2].isdigit() and text[2] == ':' and text[3:5].isdigit() and "P2P" not in text:
            
            # Se c'erano flussi accumulati per l'evento precedente, li scriviamo in formato M3U strutturato
            if current_event and event_streams:
                # Dizionario per contare quanti link abbiamo per ogni singola lingua
                lang_counts = {}
                for stream in event_streams:
                    lang = stream['lang']
                    lang_counts[lang] = lang_counts.get(lang, 0) + 1
                
                # Dizionario per tenere traccia del numero progressivo attuale durante la scrittura
                lang_current_index = {}
                
                for stream in event_streams:
                    lang = stream['lang']
                    link = stream['url']
                    
                    # Se per questa lingua c'è più di un link, aggiungiamo il numero progressivo (es. IT 1, IT 2)
                    if lang_counts[lang] > 1:
                        lang_current_index[lang] = lang_current_index.get(lang, 0) + 1
                        display_name = f"{lang} {lang_current_index[lang]}"
                    else:
                        # Se è unico, scrive solo la lingua (es. IT)
                        display_name = lang
                    
                    # LOGICA ANNIDATA: group-title crea la cartella col nome della partita.
                    m3u_lines.append(f'#EXTINF:0 group-title="{current_event}", {display_name}')
                    m3u_lines.append(link)
                    
                event_streams = []
            
            # Pulizia sicura del titolo senza tagliare via caratteri o sport
            for word in ["Guarda", "Play", "Nome", "Lingua", "Tipo"]:
                if word in text:
                    text = text.split(word)[0].strip()
            
            current_event = text.strip()
            
        # Se siamo dentro ad un evento attivo, raccogliamo i canali e le rispettive lingue
        elif current_event:
            detected_lang = "ND"
            
            # Estrazione della lingua dalle celle adiacenti
            cells = [c.get_text(strip=True) for c in el.find_all(['td', 'span'])]
            for cell in cells:
                if cell.lower() in ['it', 'es', 'en', 'pt', 'ar', 'fr', 'de', 'ru', 'pl', 'sr', 'nl', 'ro', 'lv', 'et', 'el']:
                    detected_lang = cell.upper()
                    break

            links = el.find_all('a')
            for link in links:
                href = link.get('href')
                if href and not href.startswith('javascript:') and 'rojadirecta' not in href:
                    if "creativecommons.org" in href or "google.com" in href:
                        continue
                        
                    full_url = urljoin(url, href)
                    
                    # Evitiamo duplicati identici (stesso link + stessa lingua per lo stesso evento)
                    if not any(s['url'] == full_url and s['lang'] == detected_lang for s in event_streams):
                        event_streams.append({'url': full_url, 'lang': detected_lang})

    # Scriviamo l'ultimo evento rimasto in memoria alla fine del ciclo
    if current_event and event_streams:
        lang_counts = {}
        for stream in event_streams:
            lang = stream['lang']
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
            
        lang_current_index = {}
        for stream in event_streams:
            lang = stream['lang']
            if lang_counts[lang] > 1:
                lang_current_index[lang] = lang_current_index.get(lang, 0) + 1
                display_name = f"{lang} {lang_current_index[lang]}"
            else:
                display_name = lang
                
            m3u_lines.append(f'#EXTINF:0 group-title="{current_event}", {display_name}')
            m3u_lines.append(stream['url'])

    # Salvataggio del file .m3u
    final_m3u_content = "\n".join(m3u_lines)
    with open(m3u_path, "w", encoding="utf-8") as f:
        f.write(final_m3u_content)
        
    absolute_m3u_path = os.path.abspath(m3u_path)
    print("\n==================================================")
    print("   LISTA IPTV INTELLIGENTE GENERATA CON SUCCESSO! ")
    print("==================================================")
    print(f"File salvato in: {absolute_m3u_path}")

except Exception as e:
    print(f"Errore riscontrato: {e}")
