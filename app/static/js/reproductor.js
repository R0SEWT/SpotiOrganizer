let MyEmbedController = null;
let IFrameAPI_ = null;

let btnStopPlay = null, btnNext = null, btnPrev = null;
let bolitaReproductor = null, bolitaClick = false, offsetBolita = null;
let baraProgresoActual = null

let btnLike = null, btnShuffle = null, btnRepeat = null;

let songImg = null, songTitle = null, songArtist = null, songDuration = null;

let recomendaciones = [], recomendaciones_org = []

let svg_stop = null, svg_play = null
let playing = false
let currentID = ID, currentTitle = TITLE, currentArtist = ARTIST;

document.addEventListener('DOMContentLoaded', () => {
  guardarHistorial(ID, TITLE, ARTIST)
  
  const tiempos = document.getElementsByClassName("duracion")
  for (const tiempo of tiempos) {
    tiempo.innerHTML = formatoTiempo(tiempo.innerHTML)
  }
  
  btnStopPlay = document.getElementById('btnPlay');
  btnNext = document.getElementById('btnNext');
  btnPrev = document.getElementById('btnPrev');

  svg_stop = document.getElementById('svg_stop')
  svg_play = document.getElementById('svg_play')

  obtener_recomendaciones()
  
  btnLike = document.getElementById("btnLike")
  btnShuffle = document.getElementById("btnShuffle")
  
  songImg = document.getElementById('songImg')
  songTitle = document.getElementById('songTitle')
  songArtist = document.getElementById('songArtist')
  songDuration = document.getElementById('songDuration')

  bolitaReproductor = document.getElementById('bolitaReproductor')
  baraProgresoActual = document.getElementById('barraProgresoActual')
  
  initListeners()
})

window.addEventListener("beforeunload", (e)=>{
  if(window.EmbedInfo.position < window.EmbedInfo.duration * .10 || !window.EmbedInfo){
    console.log("se omite")
    se_omite()
  }
})

function initListeners(){
  btnStopPlay.addEventListener('click', () => MyEmbedController.togglePlay())

  btnLike.addEventListener('click', () => {
    btnLike.classList.toggle("bg-red-500")
    btnLike.classList.toggle("text-white")

    const likes = JSON.parse(localStorage.getItem("likes")) ?? {}
    if(likes[currentID]) delete likes[currentID]
    else likes[currentID] = [currentTitle, currentArtist]
    
    localStorage.setItem("likes", JSON.stringify(likes))

    fetch("/agregar-favoritos", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        id: currentID,
      })
    })
    .then(res => {
      if(res.status == 401) return {status: true}
      return res.json()
    })
    .then(data => {
      if(!data.status || !data) {
        btnLike.classList.remove("bg-red-500")
        btnLike.classList.remove("text-white")
      }
    })
  })

  btnShuffle.addEventListener('click', () => {
    btnShuffle.classList.toggle("bg-purple-500", true)
    btnShuffle.classList.toggle("text-white")
    
    
    if(btnShuffle.classList.contains("text-white")){
      recomendaciones_org = recomendaciones
      recomendaciones = shuffle(recomendaciones)
    }
    else recomendaciones = recomendaciones_org

  })

  btnNext.addEventListener('click', () => nextSong())

  bolitaReproductor.addEventListener('mousedown', (e)=> {
    bolitaClick = true 
    offsetBolita = bolitaReproductor.offsetLeft - e.clientX
  })
  bolitaReproductor.addEventListener('mouseup', (e)=> bolitaClick = false)

  bolitaReproductor.addEventListener('mousemove', (e)=>{
    if(bolitaClick){
      bolitaReproductor.style.left
      const x = e.clientX;
      bolitaReproductor.style.left = (x + offsetBolita) + 'px';
      baraProgresoActual.style.width = (x + offsetBolita) + 'px';
    }
  })
}

window.onSpotifyIframeApiReady = (IFrameAPI) => {
  IFrameAPI_ = IFrameAPI
  iniciarReprooductor(URI)
};

function stopPlayer(){
  svg_play.classList.remove("hidden")
  svg_stop.classList.add("hidden")
  playing = false
}

function playPlayer(){
  svg_play.classList.add("hidden")
  svg_stop.classList.remove("hidden")
  playing = true
}

function iniciarReprooductor(uri){
  const element = document.getElementById('embed-iframe');
  const options = {
    width: '0',
    height: '0',
    uri: uri
  };
  const callback = (EmbedController) => {
    MyEmbedController = EmbedController;
    
    EmbedController.play()

    EmbedController.addListener('playback_update', e => {
      const {isPaused, isBuffering, position, duration} = e.data;
      if(playing && isPaused) stopPlayer()
      else if(!playing && !isPaused) playPlayer()
      
      actualizar_reproductor(position, duration)
    });
  };
  IFrameAPI_.createController(element, options, callback);
}

function actualizar_reproductor(position, duration){
  window.EmbedInfo = {position, duration}
  const x = position / duration * 100;
  bolitaReproductor.style.left = (x + offsetBolita) + '%';
  baraProgresoActual.style.width = (x + offsetBolita) + '%';
  document.getElementById('progressTimestamp').innerText = formatoTiempo(position);
}

async function obtener_recomendaciones() {
  const historial = JSON.parse(localStorage.getItem("historial"))
  console.log({
    "historial": Object.values(historial),
    "nombre_cancion": TITLE,
    "artista": ARTIST,
  })
  const req = await fetch("/recomendar", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "historial": Object.values(historial),
      "nombre_cancion": TITLE,
      "artista": ARTIST,
    })
  })

  const res = await req.json()
  recomendaciones = res
  showRecomendaciones(res)
}

function nextSong() {
  const cancion = recomendaciones.shift()
  const { uri, id, title, artist} = cancion
  const div = document.createElement("div")
  div.id = "embed-iframe"
  document.body.appendChild(div)

  window.history.pushState(null, "", id);
  currentArtist = artist, currentID = id, currentTitle = title

  iniciarReprooductor(uri)
  updateView(cancion)
  guardarHistorial(id, title, artist)
}

function updateView(song){
  const { artist, duration, id, img, title } = song

  songArtist.innerHTML = artist
  songDuration.innerHTML = formatoTiempo(duration)
  songImg.src = img
  songTitle.innerHTML = title
}

function showRecomendaciones(data){
  let temp = ""
  for (const { id, title, artist, duration } of data) {
    temp += `<div class="w-full grid grid-cols-6 items-center gap-2">
      <div class="col-span-1">    
        <button id="${id}" onclick="location.href='./${id}'"class="inline-flex border items-center text-white justify-center whitespace-nowrap text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:bg-white hover:text-black h-10 w-10 rounded-full">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
          <span class="sr-only">Play</span>
        </button>
      </div>
      <div class="col-span-4 flex items-center gap-2 text-sm">
        <div class="grid gap-1.5">
          <a class="text-sm font-semibold hover:underline hover:text-gray-400 text-gray-300" href="./${id}">
            ${title}
          </a>
          <a class="text-xs font-medium hover:underline hover:text-gray-400 text-gray-300" href="#">
            ${artist}
          </a>
        </div>
      </div>
      <div class="col-span-1 flex justify-end text-sm text-gray-200">
        <span>${formatoTiempo(duration)}</span>
      </div>
    </div>`
  }
  document.getElementById("recomendaciones").innerHTML = temp
}

function guardarHistorial(id, title, artist) {
  const historial = JSON.parse(localStorage.getItem("historial")) || {}
  if (!historial[id]) {
    historial[id] = [title, artist]
  }
  localStorage.setItem("historial", JSON.stringify(historial))
}

function se_omite(){
  fetch("/estadisticas/omite", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      id: currentID
    })
  })
  .then(res => res.json())
}