<!DOCTYPE html>
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

    width: 270px;
    height: 100vh;

    background: rgba(15, 23, 42, 0.97);

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


/* =========================================================
   EVENTI
   ========================================================= */

.event {

    margin-bottom: 18px;

}


.eventTitle {

    padding: 10px 8px;

    margin-bottom: 8px;

    background: #111827;

    border-radius: 6px;

    font-size: 15px;

    font-weight: bold;

    line-height: 1.3;

}


.eventTime {

    color: #22c55e;

    margin-right: 5px;

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
   MESSAGGI
   ========================================================= */

.message {

    text-align: center;

    color: #9ca3af;

    padding: 20px 5px;

    font-size: 14px;

}


.error {

    color: #ef4444;

}


/* =========================================================
   NOME CANALE
   ========================================================= */

#topBar {

    position: fixed;

    top: 15px;
    left: 290px;

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

        width: 230px;

    }

    #topBar {

        left: 250px;

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


    <div id="channelList">

        <div class="message">
            Caricamento eventi...
        </div>

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
     ZONA PER RIAPRIRE IL MENU
     ========================================================= -->

<div id="leftTrigger"></div>



<script>


/* =========================================================
   VARIABILI
   ========================================================= */

let channels = [];

let hideTimer;

let currentIndex = 0;


/* =========================================================
   ELEMENTI HTML
   ========================================================= */

const channelList =
    document.getElementById("channelList");

const player =
    document.getElementById("player");

const currentChannel =
    document.getElementById("currentChannel");

const sidebar =
    document.getElementById("sidebar");

const topBar =
    document.getElementById("topBar");


/* =========================================================
   CARICA EVENTI.JSON
   ========================================================= */

async function loadEvents() {

    try {

        console.log("====================================");
        console.log("Caricamento eventi.json...");
        console.log("====================================");


        const response =
            await fetch(
                "eventi.json?t=" + Date.now()
            );


        if (!response.ok) {

            throw new Error(
                "HTTP " + response.status
            );

        }


        const events =
            await response.json();


        console.log(
            "Eventi ricevuti:",
            events.length
        );


        /* =================================================
           CONTROLLA CHE CI SIANO EVENTI
           ================================================= */

        if (
            !Array.isArray(events) ||
            events.length === 0
        ) {

            channelList.innerHTML =
                '<div class="message">' +
                'Nessun evento trovato.' +
                '</div>';

            return;

        }


        /* =================================================
           SVUOTA LA SIDEBAR
           ================================================= */

        channelList.innerHTML = "";


        /* =================================================
           INDICE CANALE
           ================================================= */

        let globalIndex = 0;


        /* =================================================
           ELABORA GLI EVENTI
           ================================================= */

        events.forEach(function(event) {


            /* =============================================
               CONTENITORE EVENTO
               ============================================= */

            const eventContainer =
                document.createElement("div");

            eventContainer.className =
                "event";


            /* =============================================
               TITOLO EVENTO
               ============================================= */

            const eventTitle =
                document.createElement("div");

            eventTitle.className =
                "eventTitle";


            const time =
                event.time || "";


            const title =
                event.title || "Evento";


            eventTitle.innerHTML =
                '<span class="eventTime">' +
                escapeHtml(time) +
                '</span>' +
                escapeHtml(title);


            eventContainer.appendChild(
                eventTitle
            );


            /* =============================================
               CONTROLLA I CANALI
               ============================================= */

            if (
                !Array.isArray(event.channels) ||
                event.channels.length === 0
            ) {

                const noChannels =
                    document.createElement("div");

                noChannels.className =
                    "message";

                noChannels.textContent =
                    "Nessun canale disponibile";

                eventContainer.appendChild(
                    noChannels
                );


                channelList.appendChild(
                    eventContainer
                );


                return;

            }


            /* =============================================
               CREA I CANALI
               ============================================= */

            event.channels.forEach(
                function(channel) {


                    /* =====================================
                       CONTROLLO URL
                       ===================================== */

                    if (
                        !channel.watch_url
                    ) {

                        return;

                    }


                    /* =====================================
                       SALVA CANALE
                       ===================================== */

                    const channelData = {

                        name:
                            channel.name ||
                            "Canale",

                        id:
                            channel.id ||
                            "",

                        url:
                            channel.watch_url,

                        eventTitle:
                            title,

                        eventTime:
                            time

                    };


                    channels.push(
                        channelData
                    );


                    /* =====================================
                       CREA BOTTONE
                       ===================================== */

                    const button =
                        document.createElement(
                            "button"
                        );


                    button.className =
                        "channel";


                    button.textContent =
                        "▶ " +
                        channelData.name;


                    button.setAttribute(
                        "tabindex",
                        globalIndex + 1
                    );


                    /* =====================================
                       INDICE
                       ===================================== */

                    const buttonIndex =
                        globalIndex;


                    /* =====================================
                       CLICK
                       ===================================== */

                    button.onclick =
                        function() {

                            playChannel(
                                buttonIndex
                            );

                        };


                    /* =====================================
                       AGGIUNGI ALL'EVENTO
                       ===================================== */

                    eventContainer.appendChild(
                        button
                    );


                    globalIndex++;

                }
            );


            /* =============================================
               AGGIUNGI EVENTO ALLA SIDEBAR
               ============================================= */

            channelList.appendChild(
                eventContainer
            );

        });


        /* =================================================
           RISULTATO
           ================================================= */

        console.log(
            "Canali caricati:",
            channels.length
        );


        /* =================================================
           SE NON CI SONO CANALI
           ================================================= */

        if (channels.length === 0) {

            channelList.innerHTML =
                '<div class="message">' +
                'Nessun canale disponibile.' +
                '</div>';

            return;

        }


        /* =================================================
           AVVIO
           ================================================= */

        currentIndex = 0;


        const buttons =
            document.querySelectorAll(
                ".channel"
            );


        if (buttons[0]) {

            buttons[0].focus();

            buttons[0].scrollIntoView({

                behavior: "instant",

                block: "center"

            });

        }


        /*
           Non facciamo partire automaticamente
           il primo canale.

           Il player rimane vuoto finché l'utente
           non seleziona un canale.
        */


        resetHideTimer();


    }
    catch (error) {


        console.error(
            "Errore caricamento eventi:",
            error
        );


        channelList.innerHTML =
            '<div class="message error">' +
            'Errore nel caricamento degli eventi.<br><br>' +
            escapeHtml(error.message) +
            '</div>';

    }

}


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


    const channel =
        channels[index];


    /* =====================================================
       AGGIORNA INDICE
       ===================================================== */

    currentIndex =
        index;


    /* =====================================================
       CAMBIA STREAM
       ===================================================== */

    player.src =
        channel.url;


    /* =====================================================
       CAMBIA NOME
       ===================================================== */

    currentChannel.textContent =
        channel.name;


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
       PORTA IL CANALE NELLA ZONA VISIBILE
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


    console.log(
        "Riproduzione:",
        channel.name,
        channel.url
    );

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
   RESET TIMER 3 SECONDI
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
   MOUSE / TOUCH SULLA SIDEBAR
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


sidebar.addEventListener(
    "wheel",
    function() {

        showSidebar();

    }
);


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
   RIAPRI QUANDO IL MOUSE VA A SINISTRA
   ========================================================= */

document
    .getElementById("leftTrigger")
    .addEventListener(
        "mouseenter",
        function() {

            showSidebar();

        }
    );


/* =========================================================
   MOVIMENTO SULLA ZONA SINISTRA
   ========================================================= */

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
           PRENDI TUTTI I CANALI
           ================================================= */

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


        /* =================================================
           ELEMENTO ATTUALMENTE FOCALIZZATO
           ================================================= */

        const current =
            document.activeElement;


        const index =
            buttons.indexOf(
                current
            );


        /* =================================================
           QUALSIASI TASTO DI NAVIGAZIONE
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
           FRECCIA SINISTRA
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
           FRECCIA DESTRA
           ================================================= */

        if (
            event.key === "ArrowRight"
        ) {

            event.preventDefault();


            hideSidebar();


            return;

        }


        /* =================================================
           FRECCIA GIÙ
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
           FRECCIA SU
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

        loadEvents();

    }
);

</script>


</body>

</html>
