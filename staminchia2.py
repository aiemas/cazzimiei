import requests
from bs4 import BeautifulSoup
import re
import os



# ============================================================
# CONFIGURAZIONE
# ============================================================

URL = "https://dlstreams.st"

CHANNELS_URL = "https://dlstreams.st/24-7-channels.php"

OUTPUT_FILE = "index.html"



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
# FUNZIONE COSTRUZIONE URL PLAYER
# ============================================================

def build_player_url(channel_id):

    return (
        "https://dlhd.pk/embed/"
        "stream-"
        + channel_id
        + ".php"
    )



# ============================================================
# SCARICA LA PAGINA DEGLI EVENTI
# ============================================================

print("==========================================")
print("SCARICAMENTO PAGINA EVENTI...")
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
    print("ERRORE durante il download della pagina eventi:")
    print(e)
    input("\nPremi INVIO per uscire...")
    exit()



html = response.text

print()
print("Pagina eventi scaricata correttamente.")
print("Caratteri HTML:", len(html))



# ============================================================
# PARSING PAGINA EVENTI
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



            # ------------------------------------------------
            # COSTRUISCE URL PLAYER
            # ------------------------------------------------

            final_url = build_player_url(
                channel_id
            )



        else:

            channel_id = ""

            final_url = ""



        # ----------------------------------------------------
        # AGGIUNGE CANALE
        # ----------------------------------------------------

        if final_url:

            channels.append({

                "name": channel_name,

                "id": channel_id,

                "watch_url": final_url

            })



    # --------------------------------------------------------
    # SALVA EVENTO
    # --------------------------------------------------------

    if channels:

        events.append({

            "time": event_time,

            "title": event_title,

            "channels": channels

        })



# ============================================================
# SCARICA LA PAGINA CANALI 24/7
# ============================================================

print()
print("==========================================")
print("SCARICAMENTO PAGINA CANALI 24/7...")
print("URL:", CHANNELS_URL)
print("==========================================")

try:

    response_channels = requests.get(
        CHANNELS_URL,
        headers=HEADERS,
        timeout=30
    )

    response_channels.raise_for_status()

except Exception as e:

    print()
    print("ERRORE durante il download dei canali 24/7:")
    print(e)
    input("\nPremi INVIO per uscire...")
    exit()



channels_html = response_channels.text

print()
print("Pagina canali 24/7 scaricata correttamente.")
print("Caratteri HTML:", len(channels_html))



# ============================================================
# PARSING PAGINA CANALI 24/7
# ============================================================

channels_soup = BeautifulSoup(
    channels_html,
    "html.parser"
)



# ============================================================
# TROVA I CANALI 24/7
# ============================================================

channels_247 = []

channel_cards = channels_soup.select(
    "div.grid a.card"
)



print()
print("Canali 24/7 trovati:", len(channel_cards))
print()



# ============================================================
# ELABORA I CANALI 24/7
# ============================================================

for card in channel_cards:

    # --------------------------------------------------------
    # NOME CANALE
    # --------------------------------------------------------

    title_element = card.select_one(
        ".card__title"
    )

    if title_element:

        channel_name = title_element.get_text(
            " ",
            strip=True
        )

    else:

        channel_name = ""



    # --------------------------------------------------------
    # HREF
    # --------------------------------------------------------

    href = card.get(
        "href",
        ""
    )



    # --------------------------------------------------------
    # ID
    # --------------------------------------------------------

    match = re.search(
        r"[?&]id=(\d+)",
        href
    )



    if match:

        channel_id = match.group(1)



        # ----------------------------------------------------
        # URL PLAYER
        # ----------------------------------------------------

        final_url = build_player_url(
            channel_id
        )



    else:

        channel_id = ""

        final_url = ""



    # --------------------------------------------------------
    # SALVA CANALE
    # --------------------------------------------------------

    if (
        channel_name
        and
        channel_id
        and
        final_url
    ):

        channels_247.append({

            "name": channel_name,

            "id": channel_id,

            "url": final_url

        })



# ============================================================
# RISULTATI SCRAPING EVENTI
# ============================================================

print("==========================================")
print("EVENTI ELABORATI")
print("==========================================")
print()

total_event_channels = 0



for event in events:

    print(
        f'[{event["time"]}] '
        f'{event["title"]}'
    )



    for channel in event["channels"]:

        print(
            f'    - {channel["name"]}'
            f' | ID: {channel["id"]}'
            f' | URL: {channel["watch_url"]}'
        )

        total_event_channels += 1



    print()



print("==========================================")
print("TOTALE EVENTI:", len(events))
print(
    "TOTALE CANALI EVENTI:",
    total_event_channels
)
print("==========================================")
print()



# ============================================================
# RISULTATI SCRAPING CANALI 24/7
# ============================================================

print("==========================================")
print("CANALI 24/7 ELABORATI")
print("==========================================")
print()



for channel in channels_247:

    print(
        f'    - {channel["name"]}'
        f' | ID: {channel["id"]}'
        f' | URL: {channel["url"]}'
    )



print()
print("==========================================")
print(
    "TOTALE CANALI 24/7:",
    len(channels_247)
)
print("==========================================")
print()



# ============================================================
# FUNZIONE ESCAPE JAVASCRIPT
# ============================================================

def js_escape(text):

    text = str(text)

    text = text.replace("\\", "\\\\")
    text = text.replace("'", "\\'")
    text = text.replace("\r", "")
    text = text.replace("\n", "\\\n")

    return text



# ============================================================
# COSTRUISCE ARRAY JAVASCRIPT EVENTI
# ============================================================

javascript_events = []



for event in events:

    javascript_channels = []



    for channel in event["channels"]:

        javascript_channels.append(
            "{"
            "name: '" +
            js_escape(channel["name"]) +
            "', "
            "id: '" +
            js_escape(channel["id"]) +
            "', "
            "url: '" +
            js_escape(channel["watch_url"]) +
            "'"
            "}"
        )



    event_js = (
        "{"
        "time: '" +
        js_escape(event["time"]) +
        "', "
        "title: '" +
        js_escape(event["title"]) +
        "', "
        "channels: [" +
        ", ".join(javascript_channels) +
        "]"
        "}"
    )



    javascript_events.append(
        event_js
    )



events_javascript = (
    "[\n" +
    ",\n".join(javascript_events) +
    "\n]"
)



# ============================================================
# COSTRUISCE ARRAY JAVASCRIPT CANALI 24/7
# ============================================================

javascript_247_channels = []



for channel in channels_247:

    javascript_247_channels.append(
        "{"
        "name: '" +
        js_escape(channel["name"]) +
        "', "
        "id: '" +
        js_escape(channel["id"]) +
        "', "
        "url: '" +
        js_escape(channel["url"]) +
        "'"
        "}"
    )



channels_247_javascript = (
    "[\n" +
    ",\n".join(javascript_247_channels) +
    "\n]"
)



# ============================================================
# CREA INDEX.HTML
# ============================================================

html_output = r'''<!DOCTYPE html>
<html lang="it">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>TV Player</title>



<style>

/* =========================================================
   BASE
   ========================================================= */

* {
    box-sizing: border-box;
}

html,
body {

    margin: 0;
    padding: 0;

    width: 100%;
    height: 100%;

    background: #000;

    color: white;

    font-family: Arial, sans-serif;

    overflow: hidden;

}



/* =========================================================
   PLAYER
   ========================================================= */

#playerContainer {

    position: fixed;

    left: 0;
    top: 0;

    width: 100%;
    height: 100%;

    background: #000;

    z-index: 1;

}



#player {

    width: 100%;
    height: 100%;

    border: 0;

    background: #000;

}



/* =========================================================
   SIDEBAR
   ========================================================= */

#sidebar {

    position: fixed;

    left: 0;
    top: 0;

    width: 380px;
    height: 100vh;

    background: rgba(15, 23, 42, 0.40);

    padding: 15px;

    overflow-y: auto;

    z-index: 1000;

    transform: translateX(0);

    transition: transform 0.35s ease;

    box-shadow: 5px 0 20px rgba(0,0,0,0.5);

}


/* =========================================================
   SIDEBAR NASCOSTA
   ========================================================= */

#sidebar.hidden {

    transform: translateX(-100%);

}



/* =========================================================
   TITOLO
   ========================================================= */

#sidebar h1 {

    margin: 5px 0 15px 0;

    text-align: center;

    font-size: 22px;

}



/* =========================================================
   NAVIGAZIONE EVENTI / CANALI
   ========================================================= */

#menuTabs {

    display: flex;

    width: 100%;

    gap: 6px;

    margin-bottom: 12px;

}



.menuTab {

    flex: 1;

    padding: 12px 8px;

    background: rgba(255, 255, 255, 0.04);

    border: 2px solid transparent;

    border-radius: 10px;

    color: #94a3b8;

    font-size: 14px;

    font-weight: bold;

    cursor: pointer;

    /* Transizione fluida e cinematografica */
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);

}

/* Scheda attualmente attiva/selezionata */
.menuTab.active {

    background: rgba(255, 255, 255, 0.15);

    border-color: rgba(255, 255, 255, 0.4);

    color: #ffffff;

}

/* Quando passi sopra con il telecomando o il mouse (Glow cinematografico) */
.menuTab:focus,
.menuTab:hover {

    outline: none;

    background: #ffffff;

    color: #000000;

    border-color: #ffffff;

    /* Effetto zoom leggero e bagliore soffuso */
    transform: scale(1.03);

    box-shadow: 0 0 20px rgba(255, 255, 255, 0.4);

}




/* =========================================================
   RICERCA
   ========================================================= */

#searchBox {

    width: 100%;

    padding: 12px;

    margin-bottom: 15px;

    background: rgba(31, 41, 55, 0.35);

    border: 2px solid #374151;

    border-radius: 8px;

    color: white;

    font-size: 16px;

    outline: none;

}



#searchBox:focus {

    border-color: white;

    background: #374151;

}



#searchBox::placeholder {

    color: #9ca3af;

}



/* =========================================================
   EVENTO
   ========================================================= */

.event {

    margin-bottom: 18px;

}



.eventTitle {

    padding: 10px;

    margin-bottom: 6px;

    background: #111827;

    border-radius: 6px;

    font-size: 15px;

    font-weight: bold;

    line-height: 1.3;

}



.eventTime {

    color: #22c55e;

    margin-right: 6px;

}



/* =========================================================
   STILE CINEMATOGRAFICO CANALI (EVENTI E 24/7)
   ========================================================= */

.channel, 
.channel247 {


    width: 100%;

    display: block;

    margin-bottom: 8px;

    padding: 14px 16px;

    background: rgba(255, 255, 255, 0.04);

    border: 2px solid transparent;

    border-radius: 10px;

    color: #e2e8f0;

    font-size: 15px;

    font-weight: 500;

    cursor: pointer;

    text-align: left;

    /* Transizione fluida per l'effetto illuminazione */
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);

    position: relative;

    overflow: hidden;

}

.channel { display: none; }

/* Canale attualmente in riproduzione (Active) */
.channel.active, 
.channel247.active {

    background: rgba(255, 255, 255, 0.1);

    border-color: rgba(255, 255, 255, 0.3);

    color: #ffffff;

}

/* Indicatore laterale per il canale attivo */
.channel.active::before,
.channel247.active::before {

    content: "";

    position: absolute;

    left: 0;
    top: 25%;

    width: 4px;
    height: 50%;

    background: #ffffff;

    border-radius: 0 4px 4px 0;

}

/* Selezione con telecomando o Mouse Hover (Glow cinematografico) */
.channel:focus, 
.channel247:focus,
.channel:hover,
.channel247:hover {

    outline: none;

    background: #ffffff;

    color: #000000;

    border-color: #ffffff;

    /* Effetto zoom leggero per dare profondità */
    transform: scale(1.02);

    /* Bagliore d'ombra soffuso (Glow) */
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.4);

    font-weight: bold;

}



/* =========================================================
   CONTENITORI LISTE
   ========================================================= */

#eventList,
#channel247List {

    width: 100%;

}



.hiddenList {

    display: none;

}



/* =========================================================
   MESSAGGIO
   ========================================================= */

.message {

    text-align: center;

    color: #9ca3af;

    padding: 20px;

    font-size: 14px;

}



/* =========================================================
   NOME CANALE
   ========================================================= */

#topBar {

    position: fixed;

    top: 15px;
    left: 400px;

    z-index: 900;

    background: rgba(0,0,0,0.65);

    padding: 8px 15px;

    border-radius: 6px;

    font-size: 18px;

    font-weight: bold;

    transition: opacity 0.3s ease;

}



#topBar.hidden {

    opacity: 0;

}



/* =========================================================
   ZONA INVISIBILE PER RIAPRIRE IL MENU
   ========================================================= */

#leftTrigger {

    position: fixed;

    left: 0;
    top: 0;

    width: 25px;
    height: 100vh;

    z-index: 800;

}



/* =========================================================
   BOTTONE CHIUDI
   ========================================================= */

#closeMenu {

    position: absolute;

    top: 10px;
    right: 10px;

    background: #374151;

    border: none;

    color: white;

    width: 35px;
    height: 35px;

    border-radius: 50%;

    cursor: pointer;

    font-size: 18px;

}



/* =========================================================
   RESPONSIVE
   ========================================================= */

@media (max-width: 700px) {

    #sidebar {

        width: 320px;

    }

    #topBar {

        left: 340px;

    }

}

</style>

</head>



<body>



<!-- =========================================================
     PLAYER
     ========================================================= -->

<div id="playerContainer">

    <iframe
        id="player"
        src="about:blank"
        allow="autoplay; fullscreen; picture-in-picture"
        allowfullscreen>
    </iframe>

</div>



<!-- =========================================================
     SIDEBAR
     ========================================================= -->

<div id="sidebar">

    <button
        id="closeMenu"
        onclick="hideSidebar()">

        ×

    </button>



    <h1 id="sidebarTitle">📺 EVENTI</h1>



    <!-- =====================================================
         MENU EVENTI / CANALI
         ===================================================== -->

    <div id="menuTabs">

        <button
            id="eventsTab"
            class="menuTab active"
            tabindex="1"
            onclick="showEvents()">

            📅 EVENTI

        </button>



        <button
            id="channelsTab"
            class="menuTab"
            tabindex="2"
            onclick="showChannels()">

            📺 CANALI

        </button>

    </div>



    <!-- =====================================================
         RICERCA
         ===================================================== -->

    <input
        type="text"
        id="searchBox"
        placeholder="🔎 Cerca evento o canale..."
        autocomplete="off">



    <!-- =====================================================
         LISTA EVENTI
         ===================================================== -->

    <div id="eventList"></div>



    <!-- =====================================================
         LISTA CANALI 24/7
         ===================================================== -->

    <div
        id="channel247List"
        class="hiddenList">
    </div>

</div>



<!-- =========================================================
     NOME CANALE
     ========================================================= -->

<div id="topBar">

    <span id="currentChannel">
        Nessun canale
    </span>

</div>



<!-- =========================================================
     ZONA RIAPERTURA
     ========================================================= -->

<div id="leftTrigger"></div>



<script>



/* =========================================================
   DATI GENERATI AUTOMATICAMENTE DAL PYTHON
   ========================================================= */

const events = '''

html_output += events_javascript

html_output += r''';



const channels247 = '''

html_output += channels_247_javascript

html_output += r''';



/* =========================================================
   CANALI EVENTI
   ========================================================= */

const channels = [];



/* =========================================================
   ELEMENTI
   ========================================================= */

const eventList =
    document.getElementById("eventList");

const channel247List =
    document.getElementById("channel247List");

const searchBox =
    document.getElementById("searchBox");

const player =
    document.getElementById("player");

const currentChannel =
    document.getElementById("currentChannel");

const sidebar =
    document.getElementById("sidebar");

const topBar =
    document.getElementById("topBar");

const sidebarTitle =
    document.getElementById("sidebarTitle");

const eventsTab =
    document.getElementById("eventsTab");

const channelsTab =
    document.getElementById("channelsTab");



/* =========================================================
   STATO
   ========================================================= */

let currentIndex = 0;

let currentMode = "events";



/* =========================================================
   CREA LISTA EVENTI
   ========================================================= */

let globalIndex = 0;

events.forEach(function(event) {

    const eventContainer =
        document.createElement("div");

    eventContainer.className =
        "event";

    /* =====================================================
       TITOLO EVENTO (Cliccabile per espandere/comprimere)
       ===================================================== */
    const eventTitle =
        document.createElement("div");

    eventTitle.className =
        "eventTitle";

    // Rende il titolo selezionabile tramite telecomando/tastiera
    eventTitle.setAttribute("tabindex", "0");
    eventTitle.style.cursor = "pointer";

    eventTitle.innerHTML =
        '<span class="eventTime">' +
        escapeHtml(event.time) +
        '</span>' +
        escapeHtml(event.title) +
        ' <span class="arrow-indicator" style="float: right;">▼</span>';

    eventContainer.appendChild(
        eventTitle
    );

    // Array per memorizzare i bottoni dei canali di QUESTO specifico evento
    const eventButtons = [];

    /* =====================================================
       CANALI EVENTO
       ===================================================== */
    event.channels.forEach(
        function(channel) {

            const channelIndex =
                globalIndex;

            channels.push({
                name: channel.name,
                id: channel.id,
                url: channel.url,
                eventTitle: event.title,
                eventTime: event.time
            });

            const button =
                document.createElement(
                    "button"
                );

            button.className =
                "channel";

            button.textContent =
                "▶ " + channel.name;

            button.setAttribute(
                "tabindex",
                "0"
            );

            button.onclick =
                function() {
                    playEventChannel(
                        channelIndex
                    );
                };

            eventContainer.appendChild(
                button
            );

            // Salviamo il bottone nell'elenco locale di questo evento
            eventButtons.push(button);
            globalIndex++;

        }
    );

    // FUNZIONE INTERNA PER MOSTRARE/NASCONDERE I CANALI DI QUESTO EVENTO
    function toggleEvent() {
        const isCurrentlyHidden = eventButtons.length > 0 && (eventButtons[0].style.display === "" || eventButtons[0].style.display === "none");
        const indicator = eventTitle.querySelector(".arrow-indicator");

        eventButtons.forEach(function(button) {
            button.style.display = isCurrentlyHidden ? "block" : "none";
        });

        if (indicator) {
            indicator.textContent = isCurrentlyHidden ? "▲" : "▼";
        }
    }

    // Collega la funzione al click del mouse e alla pressione dei tasti OK/Enter
    eventTitle.onclick = toggleEvent;
    eventTitle.onkeydown = function(e) {
        if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            toggleEvent();
        }
    };

    eventList.appendChild(
        eventContainer
    );

});




/* =========================================================
   CREA LISTA CANALI 24/7
   ========================================================= */

channels247.forEach(
    function(channel, index) {



        const button =
            document.createElement(
                "button"
            );



        button.className =
            "channel247";



        button.textContent =
            "▶ " + channel.name;



        button.setAttribute(
            "tabindex",
            "0"
        );



        button.onclick =
            function() {

                play247Channel(
                    index
                );

            };



        channel247List.appendChild(
            button
        );

    }
);



/* =========================================================
   RICERCA
   ========================================================= */

searchBox.addEventListener(
    "input",
    function() {

        const search =
            searchBox.value
                .toLowerCase()
                .trim();



        if (currentMode === "events") {

            const eventContainers =
                document.querySelectorAll(
                    "#eventList .event"
                );



            eventContainers.forEach(
                function(container) {

                    const text =
                        container.textContent
                            .toLowerCase();

                    if (
                        text.includes(search)
                    ) {

                        container.style.display =
                            "";

                    }
                    else {

                        container.style.display =
                            "none";

                    }

                }
            );

        }
        else {

            const buttons =
                document.querySelectorAll(
                    "#channel247List .channel247"
                );



            buttons.forEach(
                function(button) {

                    const text =
                        button.textContent
                            .toLowerCase();

                    if (
                        text.includes(search)
                    ) {

                        button.style.display =
                            "";

                    }
                    else {

                        button.style.display =
                            "none";

                    }

                }
            );

        }

    }
);



/* =========================================================
   ESCAPE HTML
   ========================================================= */

function escapeHtml(text) {

    const div =
        document.createElement("div");



    div.textContent =
        text;



    return div.innerHTML;

}



/* =========================================================
   MOSTRA EVENTI
   ========================================================= */

function showEvents() {

    currentMode =
        "events";



    sidebarTitle.textContent =
        "📺 EVENTI";



    eventList.classList.remove(
        "hiddenList"
    );



    channel247List.classList.add(
        "hiddenList"
    );



    eventsTab.classList.add(
        "active"
    );



    channelsTab.classList.remove(
        "active"
    );



    searchBox.value =
        "";



    const eventContainers =
        document.querySelectorAll(
            "#eventList .event"
        );



    eventContainers.forEach(
        function(container) {

            container.style.display =
                "";

        }
    );



    const buttons =
        document.querySelectorAll(
            "#eventList .channel"
        );



    if (buttons.length > 0) {

        if (
            buttons[currentIndex]
        ) {

            buttons[currentIndex].focus();

            buttons[currentIndex].scrollIntoView({

                behavior: "instant",

                block: "center"

            });

        }

    }

}



/* =========================================================
   MOSTRA CANALI
   ========================================================= */

function showChannels() {

    currentMode =
        "channels";



    sidebarTitle.textContent =
        "📺 CANALI 24/7";



    eventList.classList.add(
        "hiddenList"
    );



    channel247List.classList.remove(
        "hiddenList"
    );



    eventsTab.classList.remove(
        "active"
    );



    channelsTab.classList.add(
        "active"
    );



    searchBox.value =
        "";



    const buttons =
        document.querySelectorAll(
            "#channel247List .channel247"
        );



    buttons.forEach(
        function(button) {

            button.style.display =
                "";

        }
    );



        // Trova questo blocco dentro showChannels() e modificalo così:
    if (buttons.length > 0) {
        
        // Sostituisci buttons[0] con la gestione di currentIndex:
        let indexToFocus = (currentIndex < buttons.length) ? currentIndex : 0;

        buttons[indexToFocus].focus();

        buttons[indexToFocus].scrollIntoView({

            behavior: "instant",

            block: "center"

        });

    }


}



/* =========================================================
   RIPRODUCI CANALE EVENTO
   ========================================================= */

function playEventChannel(index) {

    if (
        index < 0 ||
        index >= channels.length
    ) {

        return;

    }



    currentIndex =
        index;



    player.src =
        channels[index].url;



    currentChannel.textContent =
        channels[index].name;



    const buttons =
        document.querySelectorAll(
            "#eventList .channel"
        );



    buttons.forEach(
        function(button) {

            button.classList.remove(
                "active"
            );

        }
    );



    if (buttons[index]) {

        buttons[index].classList.add(
            "active"
        );

    }



    if (buttons[index]) {

        buttons[index].scrollIntoView({

            behavior: "smooth",

            block: "center"

        });

    }



    hideSidebar();

}



/* =========================================================
   RIPRODUCI CANALE 24/7
   ========================================================= */

function play247Channel(index) {

    if (
        index < 0 ||
        index >= channels247.length
    ) {

        return;

    }

    // AGGIUNGI QUESTA RIGA PER SALVARE L'INDICE ATTUALE:
    currentIndex = index;

    player.src =
        channels247[index].url;




    player.src =
        channels247[index].url;



    currentChannel.textContent =
        channels247[index].name;



    const buttons =
        document.querySelectorAll(
            "#channel247List .channel247"
        );



    buttons.forEach(
        function(button) {

            button.classList.remove(
                "active"
            );

        }
    );



    if (buttons[index]) {

        buttons[index].classList.add(
            "active"
        );

    }



    if (buttons[index]) {

        buttons[index].scrollIntoView({

            behavior: "smooth",

            block: "center"

        });

    }



    hideSidebar();

}



/* =========================================================
   MOSTRA SIDEBAR
   ========================================================= */

function showSidebar() {

    sidebar.classList.remove(
        "hidden"
    );

    topBar.classList.remove(
        "hidden"
    );

    setTimeout(function() {

        // MODIFICA QUESTO BLOCCO:
        let buttons;
        if (currentMode === "events") {
            buttons = document.querySelectorAll("#eventList .channel");
        } else {
            buttons = document.querySelectorAll("#channel247List .channel247");
        }

        if (buttons && buttons[currentIndex]) {

            buttons[currentIndex].focus();

            buttons[currentIndex].scrollIntoView({
                behavior: "instant",
                block: "center"
            });

        }

    }, 50);

}




/* =========================================================
   NASCONDE SIDEBAR
   ========================================================= */

function hideSidebar() {

    sidebar.classList.add(
        "hidden"
    );

    topBar.classList.add(
        "hidden"
    );

}



/* =========================================================
   ZONA SINISTRA
   ========================================================= */

document
    .getElementById("leftTrigger")
    .addEventListener(
        "mouseenter",
        function() {

            showSidebar();

        }
    );



document
    .getElementById("leftTrigger")
    .addEventListener(
        "mousemove",
        function() {

            showSidebar();

        }
    );



/* =========================================================
   TELECOMANDO / TASTIERA
   ========================================================= */

document.addEventListener(
    "keydown",
    function(event) {

        /* =================================================
           SIDEBAR NASCOSTA

           QUALSIASI TASTO RIAPRE IL MENU
           ================================================= */

        if (
            sidebar.classList.contains(
                "hidden"
            )
        ) {

            showSidebar();



            if (
                currentMode === "events"
            ) {

                const buttons =
                    Array.from(
                        document.querySelectorAll(
                            "#eventList .channel"
                        )
                    );



                if (
                    buttons[currentIndex]
                ) {

                    buttons[currentIndex].focus();

                    buttons[currentIndex].scrollIntoView({

                        behavior: "instant",

                        block: "center"

                    });

                }

            }
            else {

                const buttons =
                    Array.from(
                        document.querySelectorAll(
                            "#channel247List .channel247"
                        )
                    );



                if (buttons.length > 0) {

                    buttons[0].focus();

                    buttons[0].scrollIntoView({

                        behavior: "instant",

                        block: "center"

                    });

                }

            }



            return;

        }



        /* =================================================
           TAB ATTIVI
           ================================================= */

        if (
            document.activeElement === eventsTab ||
            document.activeElement === channelsTab
        ) {

            if (
                event.key === "ArrowLeft"
            ) {

                event.preventDefault();

                eventsTab.focus();

                return;

            }



            if (
                event.key === "ArrowRight"
            ) {

                event.preventDefault();

                channelsTab.focus();

                return;

            }



            if (
                event.key === "ArrowDown"
            ) {

                event.preventDefault();

                if (
                    currentMode === "events"
                ) {

                    const buttons =
                        document.querySelectorAll(
                            "#eventList .channel"
                        );

                    if (buttons.length > 0) {

                        buttons[0].focus();

                    }

                }
                else {

                    const buttons =
                        document.querySelectorAll(
                            "#channel247List .channel247"
                        );

                    if (buttons.length > 0) {

                        buttons[0].focus();

                    }

                }

                return;

            }

        }



        /* =================================================
           CANALE ATTIVO
           ================================================= */

        let buttons;



        if (
            currentMode === "events"
        ) {

            buttons =
                Array.from(
                    document.querySelectorAll(
                        "#eventList .channel"
                    )
                );

        }
        else {

            buttons =
                Array.from(
                    document.querySelectorAll(
                        "#channel247List .channel247"
                    )
                );

        }



        if (
            buttons.length === 0
        ) {

            return;

        }



        const current =
            document.activeElement;



        const index =
            buttons.indexOf(
                current
            );



        /* =================================================
           SINISTRA
           ================================================= */

        if (
            event.key === "ArrowLeft"
        ) {

            event.preventDefault();

            hideSidebar();

            return;

        }



        /* =================================================
           DESTRA
           ================================================= */

        if (
            event.key === "ArrowRight"
        ) {

            event.preventDefault();

            hideSidebar();

            return;

        }



                /* =================================================
           SU (GESTIONE RISALITA SUI TAB SE SI È SUL PRIMO CANALE)
           ================================================= */

        if (
            event.key === "ArrowUp"
        ) {

            event.preventDefault();

            // Se l'utente si trova sul primo canale della lista, sale sulla scheda attiva
            if (index === 0) {
                if (currentMode === "events") {
                    eventsTab.focus();
                } else {
                    channelsTab.focus();
                }
                return;
            }

            let previous;

            if (index < 0) {

                previous =
                    buttons.length - 1;

            }
            else {

                previous =
                    index - 1;

            }

            if (
                previous < 0
            ) {

                previous =
                    buttons.length - 1;

            }

            buttons[previous].focus();

            buttons[previous].scrollIntoView({

                behavior: "smooth",

                block: "nearest"

            });

            return;

        }

        /* =================================================
           GIÙ (SCORRIMENTO FLUIDO DELLA LISTA CANALI)
           ================================================= */

        if (
            event.key === "ArrowDown"
        ) {

            event.preventDefault();

            let next;

            if (index < 0) {

                next = 0;

            }
            else {

                next =
                    index + 1;

            }

            if (
                next >= buttons.length
            ) {

                next = 0;

            }

            buttons[next].focus();

            buttons[next].scrollIntoView({

                behavior: "smooth",

                block: "nearest"

            });

            return;

        }



        /* =================================================
           ENTER / OK
           ================================================= */

        if (
            event.key === "Enter" ||
            event.key === " "
        ) {

            if (
                index >= 0
            ) {

                event.preventDefault();



                if (
                    currentMode === "events"
                ) {

                    playEventChannel(
                        index
                    );

                }
                else {

                    play247Channel(
                        index
                    );

                }

            }

        }

    }
);



/* =========================================================
   AVVIO
   ========================================================= */

window.addEventListener(
    "load",
    function() {

        console.log(
            "Eventi caricati:",
            events.length
        );



        console.log(
            "Canali eventi caricati:",
            channels.length
        );



        console.log(
            "Canali 24/7 caricati:",
            channels247.length
        );



        /* =================================================
           PRIMO CANALE EVENTO A FUOCO
           ================================================= */

        const buttons =
            document.querySelectorAll(
                "#eventList .channel"
            );



        if (buttons.length > 0) {

            currentIndex = 0;



            buttons[0].focus();



            buttons[0].scrollIntoView({

                behavior: "instant",

                block: "center"

            });

        }



        /* =================================================
           SIDEBAR VISIBILE ALL'AVVIO
           ================================================= */

        showSidebar();

    }
);



</script>



</body>

</html>
'''



# ============================================================
# SCRIVE INDEX.HTML
# ============================================================

print("==========================================")
print("CREAZIONE INDEX.HTML")
print("==========================================")

try:

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            html_output
        )

except Exception as e:

    print()
    print("ERRORE durante la creazione di index.html:")
    print(e)

    input("\nPremi INVIO per uscire...")

    exit()



# ============================================================
# CONTROLLA CHE INDEX.HTML ESISTA
# ============================================================

print()
print("Controllo file...")

if not os.path.isfile(OUTPUT_FILE):

    print()
    print("ERRORE:")
    print("index.html NON è stato creato.")
    print()

    input("Premi INVIO per uscire...")

    exit()



print()
print("==========================================")
print("index.html creato correttamente.")
print("==========================================")
print()
print("Eventi:", len(events))
print("Canali eventi:", total_event_channels)
print("Canali 24/7:", len(channels_247))
print()
