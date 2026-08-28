import requests
from bs4 import BeautifulSoup
import re
import os


# ============================================================
# CONFIGURAZIONE
# ============================================================

URL = "https://dlstreams.st/index.php?cat=All+Soccer+Events+%E2%9A%BD"

OUTPUT_FILE = "staminchiawp.m3u"


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
print("SCARICAMENTO PAGINA")
print("==========================================")
print()
print("URL:", URL)
print()

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
    print()

    input("Premi INVIO per uscire...")

    exit()


html = response.text


print("Pagina scaricata correttamente.")
print("Caratteri HTML:", len(html))
print()


# ============================================================
# PARSING HTML
# ============================================================

soup = BeautifulSoup(
    html,
    "html.parser"
)


# ============================================================
# TROVA TUTTI GLI EVENTI
# ============================================================

event_blocks = soup.select(
    "div.schedule__event"
)


print("==========================================")
print("EVENTI TROVATI:", len(event_blocks))
print("==========================================")
print()


# ============================================================
# LISTA M3U
# ============================================================

m3u_lines = []

m3u_lines.append(
    "#EXTM3U"
)


# ============================================================
# CONTATORI
# ============================================================

total_events = 0
total_channels = 0


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
    # TITOLO EVENTO
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
    # SE NON C'È TITOLO, SALTA
    # --------------------------------------------------------

    if not event_title:

        continue


    # --------------------------------------------------------
    # CREA GROUP-TITLE
    #
    # Esempio:
    #
    # 🎾 US Open : Darya vs Marina
    #
    # diventa:
    #
    # 🎾 US Open
    # --------------------------------------------------------

    if ":" in event_title:

        group_title = event_title.split(
            ":",
            1
        )[0].strip()

    else:

        group_title = event_title.strip()


    # --------------------------------------------------------
    # TROVA I CANALI DELL'EVENTO
    # --------------------------------------------------------

    channel_elements = event_block.select(
        ".schedule__channels a"
    )


    # --------------------------------------------------------
    # SE NON CI SONO CANALI
    # --------------------------------------------------------

    if not channel_elements:

        continue


    total_events += 1


    # ========================================================
    # ELABORA I CANALI
    # ========================================================

    for channel_element in channel_elements:


        # ----------------------------------------------------
        # NOME CANALE
        # ----------------------------------------------------

        channel_name = channel_element.get_text(
            " ",
            strip=True
        )


        # ----------------------------------------------------
        # HREF ORIGINALE
        # ----------------------------------------------------

        href = channel_element.get(
            "href",
            ""
        ).strip()


        # ----------------------------------------------------
        # ESTRAE ID
        #
        # Accetta:
        #
        # /watch.php?id=1597
        #
        # https://dlstreams.st/watch.php?id=1597
        #
        # ecc.
        # ----------------------------------------------------

        match = re.search(
            r"[?&]id=(\d+)",
            href
        )


        if not match:

            print(
                "ATTENZIONE: link senza ID:",
                href
            )

            continue


        channel_id = match.group(1)


        # ----------------------------------------------------
        # COSTRUISCE URL ORIGINALE
        #
        # Se il sito restituisce:
        #
        # /watch.php?id=1597
        #
        # lo trasformiamo in:
        #
        # https://dlstreams.st/watch.php?id=1597
        #
        # Se invece restituisce già un URL completo,
        # manteniamo quello.
        # ----------------------------------------------------

        if href.startswith("http://"):

            final_url = href

        elif href.startswith("https://"):

            final_url = href

        elif href.startswith("//"):

            final_url = "https:" + href

        else:

            if href.startswith("/"):

                final_url = (
                    URL.rstrip("/")
                    + href
                )

            else:

                final_url = (
                    URL.rstrip("/")
                    + "/"
                    + href
                )


        # ====================================================
        # NOME COMPLETO DEL CANALE
        # ====================================================

        if channel_name:

            full_name = (
                event_time
                + " – "
                + event_title
                + " – "
                + channel_name
            )

        else:

            full_name = (
                event_time
                + " – "
                + event_title
            )


        # ====================================================
        # AGGIUNGE EXTINF
        # ====================================================

        m3u_lines.append(
            '#EXTINF:-1 group-title="'
            + group_title.replace('"', "'")
            + '",'
            + full_name.replace('"', "'")
        )


        # ====================================================
        # AGGIUNGE URL
        # ====================================================

        m3u_lines.append(
            final_url
        )


        # ====================================================
        # CONTATORE
        # ====================================================

        total_channels += 1


        # ====================================================
        # STAMPA
        # ====================================================

        print(
            "["
            + event_time
            + "] "
            + event_title
        )

        print(
            "    - "
            + channel_name
        )

        print(
            "      ID: "
            + channel_id
        )

        print(
            "      URL: "
            + final_url
        )

        print()


# ============================================================
# RISULTATI
# ============================================================

print("==========================================")
print("RISULTATI")
print("==========================================")
print()
print("EVENTI ELABORATI:", total_events)
print("CANALI TROVATI:", total_channels)
print()


# ============================================================
# CONTROLLA SE ABBIAMO TROVATO QUALCOSA
# ============================================================

if total_channels == 0:

    print("ATTENZIONE!")
    print()
    print("Non è stato trovato nessun canale.")
    print("Il file M3U non verrà creato.")
    print()

    input("Premi INVIO per uscire...")

    exit()


# ============================================================
# CREA CONTENUTO M3U
# ============================================================

m3u_content = "\n".join(
    m3u_lines
)


# ============================================================
# SCRIVE FILE M3U
# ============================================================

print("==========================================")
print("CREAZIONE FILE M3U")
print("==========================================")
print()

try:

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            m3u_content
        )

except Exception as e:

    print()
    print("ERRORE durante la creazione del file:")
    print(e)
    print()

    input("Premi INVIO per uscire...")

    exit()


# ============================================================
# CONTROLLA FILE
# ============================================================

print("Controllo file...")

if not os.path.isfile(
    OUTPUT_FILE
):

    print()
    print("ERRORE:")
    print(
        OUTPUT_FILE,
        "NON è stato creato."
    )
    print()

    input("Premi INVIO per uscire...")

    exit()


# ============================================================
# DIMENSIONE FILE
# ============================================================

file_size = os.path.getsize(
    OUTPUT_FILE
)


# ============================================================
# FINE
# ============================================================

print()
print("==========================================")
print("OPERAZIONE COMPLETATA")
print("==========================================")
print()
print(
    "File creato:",
    OUTPUT_FILE
)
print(
    "Dimensione:",
    file_size,
    "bytes"
)
print(
    "Eventi:",
    total_events
)
print(
    "Canali:",
    total_channels
)
print()
print("==========================================")
print()
print("Il file M3U è pronto per Wiseplay.")
print()
