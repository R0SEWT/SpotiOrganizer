from flask import Blueprint, render_template, current_app, request
from ..spotify import SpotifyApi

from ..algoritmo import recomendacion

from pprint import pprint

public_routes = Blueprint('public', __name__)

@public_routes.get("/")
def index():
    spotify_client:SpotifyApi = current_app.config.get("spotify_client")
    artistas = spotify_client.obtener_artistas() or []
    tracks = spotify_client.user_top_tracks(8) or []
    return render_template('index.html', artistas=artistas, tracks=tracks)

@public_routes.get("/top")
def get_top_tracks():
    spotify_client:SpotifyApi = current_app.config.get("spotify_client")
    return spotify_client.user_top_tracks(5) or []

@public_routes.get("/escuchar/<string:id>")
def escuchar(id):
    spotify_client:SpotifyApi = current_app.config.get("spotify_client")
    cancion:dict = spotify_client.obtener_cancion(id)
    
    uri = cancion["uri"]
    title = cancion.get("name")
    duration = cancion.get("duration_ms")
    url_img = cancion.get("album", {}).get("images", [{}, {}])[1].get("url", "")
    artistas =map(lambda a: a["name"], cancion.get("artists", [{}]))
    
    return render_template('reproductor.html', id=id, uri=uri, title=title, artistas=list(artistas), duration=duration, url_img=url_img)

@public_routes.post("/recomendar")
def recomendar():
    data = request.json
    historial = data.get("historial")
    nombre_cancion = data.get("nombre_cancion")
    artista = data.get("artista")

    # with open("info.json", "w") as f:
        # f.write(str(historial))

    df_user = recomendacion.crear_df_user(historial)

    res_recomendacion = recomendacion.get_best_recommendations(nombre_cancion, artista, recomendacion.matriz_similaridad, df_user)
    
    
    spotify_client:SpotifyApi = current_app.config.get("spotify_client")

    URIs = res_recomendacion[:, -1]
    canciones = spotify_client.obtener_info_canciones(URIs)
    
    return [
            {
                "id": item["id"], 
                "title": item['name'],
                "artist": item['artists'][0]['name'],
                "uri": item["uri"],
                "img": item["album"]["images"][-1]["url"],
                "duration": item["duration_ms"]
            } 
            for item in canciones["tracks"]
    ]

@public_routes.get("/buscar")
def buscar():
    args = request.args
    query = args.get("q")

    spotify_client:SpotifyApi = current_app.config.get("spotify_client")
    
    if not query:
        return render_template('busqueda.html', canciones=[])
    
    res = spotify_client.buscar_cancion(query)
    canciones = ({"id": track["id"], "title": track["name"], "img": track["album"]["images"][0]["url"], "duration": track["duration_ms"], "artist": [artist["name"] for artist in track["artists"]] } for track in res["tracks"]["items"])
    return render_template('busqueda.html', canciones=canciones)
