import requests
from bs4 import BeautifulSoup
import re
import os


# ============================================================
# CONFIGURAZIONE
# ============================================================

URL = "https://dlstreams.st"

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
    input("\nPremi INVIO per uscire...")
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


            # ------------------------------------------------
            # COSTRUISCE URL PLAYER
            # ------------------------------------------------

            final_url = (
                "https://dlhd.pk/embed/"
                "stream-"
                + channel_id
                + ".php"
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
# RISULTATI SCRAPING
# ============================================================

print("==========================================")
print("EVENTI ELABORATI")
print("==========================================")
print()

total_channels = 0


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

        total_channels += 1


    print()


print("==========================================")
print("TOTALE EVENTI:", len(events))
print("TOTALE CANALI:", total_channels)
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
    text = text.replace("\n", "\\n")

    return text


# ============================================================
# COSTRUISCE ARRAY JAVASCRIPT
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

    width: 300px;
    height: 100vh;

    background: rgba(15, 23, 42, 0.60);

    padding: 15px;

    overflow-y: auto;

    z-index: 1000;

    transform: translateX(0);

    transition: transform 0.35s ease;

    box-shadow: 5px 0 20px rgba(0,0,0,0.5);

}


/* Sidebar nascosta */

#sidebar.hidden {

    transform: translateX(-100%);

}


/* =========================================================
   TITOLO
   ========================================================= */

#sidebar h1 {

    margin: 5px 0 20px 0;

    text-align: center;

    font-size: 22px;

}

#searchBox {

    width: 100%;

    padding: 12px;

    margin-bottom: 15px;

    background: #1f2937;

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
   CANALI
   ========================================================= */

.channel {

    width: 100%;

    display: block;

    margin-bottom: 7px;

    padding: 12px 10px;

    background: #1f2937;

    border: 2px solid transparent;

    border-radius: 8px;

    color: white;

    font-size: 15px;

    cursor: pointer;

    text-align: left;

}


.channel:hover {

    background: #374151;

}


.channel:focus {

    outline: none;

    border-color: white;

    background: #16a34a;

}


.channel.active {

    background: #16a34a;

    border-color: white;

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
    left: 320px;

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

        width: 240px;

    }

    #topBar {

        left: 260px;

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


    <h1>📺 EVENTI</h1>

<input
    type="text"
    id="searchBox"
    placeholder="🔎 Cerca evento o canale..."
    autocomplete="off">

<div id="channelList"></div>


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


/* =========================================================
   CANALI
   ========================================================= */

const channels = [];


/* =========================================================
   ELEMENTI
   ========================================================= */

const channelList =
    document.getElementById("channelList");
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


/* =========================================================
   CREA LISTA EVENTI E CANALI
   ========================================================= */

let globalIndex = 0;


events.forEach(function(event) {


    /* =====================================================
       CONTENITORE EVENTO
       ===================================================== */

    const eventContainer =
        document.createElement("div");


    eventContainer.className =
        "event";


    /* =====================================================
       TITOLO EVENTO
       ===================================================== */

    const eventTitle =
        document.createElement("div");


    eventTitle.className =
        "eventTitle";


    eventTitle.innerHTML =
        '<span class="eventTime">' +
        escapeHtml(event.time) +
        '</span>' +
        escapeHtml(event.title);


    eventContainer.appendChild(
        eventTitle
    );


    /* =====================================================
       CANALI
       ===================================================== */

    event.channels.forEach(
        function(channel) {


            /* =============================================
               SALVA CANALE
               ============================================= */

            const channelIndex =
                globalIndex;


            channels.push({

                name: channel.name,

                id: channel.id,

                url: channel.url,

                eventTitle: event.title,

                eventTime: event.time

            });


            /* =============================================
               CREA PULSANTE
               ============================================= */

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
                channelIndex + 1
            );


            button.onclick =
                function() {

                    playChannel(
                        channelIndex
                    );

                };


            eventContainer.appendChild(
                button
            );


            globalIndex++;

        }
    );


    /* =====================================================
       AGGIUNGI EVENTO ALLA SIDEBAR
       ===================================================== */

    channelList.appendChild(
        eventContainer
    );

});

searchBox.addEventListener(
    "input",
    function() {

        const search =
            searchBox.value
                .toLowerCase()
                .trim();

        const eventsContainers =
            document.querySelectorAll(".event");

        eventsContainers.forEach(
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
);


/* =========================================================
   TIMER
   ========================================================= */

let hideTimer;


/* =========================================================
   INDICE CORRENTE
   ========================================================= */

let currentIndex = 0;


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
   RIPRODUCI CANALE
   ========================================================= */

function playChannel(index) {


    if (
        index < 0 ||
        index >= channels.length
    ) {

        return;

    }


    currentIndex =
        index;


    /* =====================================================
       CAMBIA STREAM
       ===================================================== */

    player.src =
        channels[index].url;


    /* =====================================================
       CAMBIA NOME
       ===================================================== */

    currentChannel.textContent =
        channels[index].name;


    /* =====================================================
       AGGIORNA SELEZIONE
       ===================================================== */

    const buttons =
        document.querySelectorAll(
            ".channel"
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


    /* =====================================================
       SCROLL
       ===================================================== */

    if (buttons[index]) {

        buttons[index].scrollIntoView({

            behavior: "smooth",

            block: "center"

        });

    }


    /* =====================================================
       MOSTRA SIDEBAR
       ===================================================== */

    showSidebar();

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


    resetHideTimer();

}


/* =========================================================
   NASCONDE SIDEBAR
   ========================================================= */

function hideSidebar() {


    clearTimeout(
        hideTimer
    );


    sidebar.classList.add(
        "hidden"
    );


    topBar.classList.add(
        "hidden"
    );

}


/* =========================================================
   RESET TIMER
   ========================================================= */

function resetHideTimer() {


    clearTimeout(
        hideTimer
    );


    hideTimer =
        setTimeout(
            function() {

                hideSidebar();

            },
            3000
        );

}


/* =========================================================
   MOUSE SULLA SIDEBAR
   ========================================================= */

sidebar.addEventListener(
    "mousemove",
    function() {

        if (
            !sidebar.classList.contains(
                "hidden"
            )
        ) {

            resetHideTimer();

        }

    }
);


/* =========================================================
   SCROLL
   ========================================================= */

sidebar.addEventListener(
    "wheel",
    function() {

        showSidebar();

    }
);


/* =========================================================
   TOUCH
   ========================================================= */

sidebar.addEventListener(
    "touchstart",
    function() {

        showSidebar();

    }
);


sidebar.addEventListener(
    "touchmove",
    function() {

        showSidebar();

    }
);


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


        const buttons =
            Array.from(
                document.querySelectorAll(
                    ".channel"
                )
            );


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
           ATTIVITÀ
           ================================================= */

        if (

            event.key === "ArrowLeft" ||

            event.key === "ArrowRight" ||

            event.key === "ArrowUp" ||

            event.key === "ArrowDown" ||

            event.key === "Enter" ||

            event.key === " "

        ) {

            showSidebar();

        }


        /* =================================================
           SINISTRA
           ================================================= */

        if (
            event.key === "ArrowLeft"
        ) {

            event.preventDefault();


            if (index < 0) {

                buttons[currentIndex].focus();

            }
            else {

                buttons[index].focus();

            }


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
           GIÙ
           ================================================= */

        if (
            event.key === "ArrowDown"
        ) {

            event.preventDefault();


            let next;


            if (index < 0) {

                next =
                    currentIndex + 1;

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


            currentIndex =
                next;


            buttons[next].focus();


            buttons[next].scrollIntoView({

                behavior: "smooth",

                block: "nearest"

            });


            return;

        }


        /* =================================================
           SU
           ================================================= */

        if (
            event.key === "ArrowUp"
        ) {

            event.preventDefault();


            let previous;


            if (index < 0) {

                previous =
                    currentIndex - 1;

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


            currentIndex =
                previous;


            buttons[previous].focus();


            buttons[previous].scrollIntoView({

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


                playChannel(
                    index
                );

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
            "Canali caricati:",
            channels.length
        );


        /* =================================================
           METTE IL PRIMO CANALE A FUOCO
           ================================================= */

        const buttons =
            document.querySelectorAll(
                ".channel"
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
           TIMER SIDEBAR
           ================================================= */

        resetHideTimer();

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
print("index.html creato correttamente.")
