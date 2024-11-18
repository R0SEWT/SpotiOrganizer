import requests
from spotipy import Spotify, util, SpotifyException
from functools import wraps 
from typing import Optional
from pprint import pprint

def renew_token_if_needed(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except SpotifyException as e:
            print(e.http_status)
            if e.http_status == 401:  # Unauthorized
                self.obtener_nuevo_token()
                return func(self, *args, **kwargs)
            else:
                raise
    return wrapper

class SpotifyApi:
    """
    Una clase para interactuar con la API de Spotify.
    
    Atributos:
        TOKEN_ENDPOINT (str): El endpoint para obtener tokens de Spotify.
        __client_id (str): El ID de cliente para la aplicación de Spotify.
        __client_secret (str): El secreto de cliente para la aplicación de Spotify.
        scope (str): El alcance de la solicitud de acceso.
        __username (str): El nombre de usuario de Spotify.
        redirect_uri (str): La URI de redirección para la aplicación de Spotify.
        spotify_client (Spotify): La instancia del cliente de Spotify.
        token (str): El token de acceso.
        refresh_token (str): El token de actualización.
    
    Métodos:
        get_url_oauth(): Genera la URL de OAuth para la autorización del usuario.
        obtener_nuevo_token(): Obtiene un nuevo token de acceso usando el token de actualización.
        req_obtener_nuevo_token(refresh_token): Solicita un nuevo token de acceso usando el token de actualización.
        obtener_token(code, code_verifier): Obtiene un token de acceso usando el código de autorización.
        init_sp_client(token): Inicializa el cliente de Spotify con el token dado.
        info_usuario(): Obtiene la información del usuario actual.
        buscar_cancion(nombre): Busca una canción por su nombre.
        user_top_tracks(top): Obtiene las canciones principales del usuario actual.
        obtener_cancion(id): Obtiene información sobre una canción específica por su ID.
        obtener_info_canciones(q): Obtiene información sobre múltiples canciones.
        obtener_artistas(): Obtiene artistas recomendados basados en géneros semilla.
    """
    TOKEN_ENDPOINT = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id:str, secret_client:str, username:str, scope:str, redirect_uri:str) -> None:
        self.__client_id = client_id
        self.__client_secret = secret_client
        self.scope = scope
        self.__username = username
        self.redirect_uri = redirect_uri
        
        self.spotify_client:Spotify = None
        self.token:str = None
        self.refresh_token:str = None

        print(self.get_url_oauth()) 
        token = util.prompt_for_user_token(self.__username, self.scope, self.__client_id, self.__client_secret, self.redirect_uri)
        self.init_sp_client(token)

    def get_url_oauth(self):
        return f"https://accounts.spotify.com/authorize?client_id={self.__client_id}&scope={self.scope}&response_type=code"
    
    def obtener_nuevo_token(self):
        if tk:=self.refresh_token:
            res = self.req_obtener_nuevo_token(tk)
            if res:
                self.refresh_token = res["refresh_token"]
                self.init_sp_client(res["access_token"])
        else:
            token = util.prompt_for_user_token(self.__username, self.scope, self.__client_id, self.__client_secret, self.redirect_uri)
            self.init_sp_client(token)
    
    def req_obtener_nuevo_token(self, refresh_token) -> Optional[dict]:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {
            "client_id": self.__client_id,
            "grant_type": "refresh_code",
            "refresh_token": refresh_token
        }
        res = requests.post(SpotifyApi.TOKEN_ENDPOINT, data=data, headers=headers)
        return res.json() if res.status_code == 200 else None

    def obtener_token(self, code, code_verifier):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        print("req redirect_uri", self.redirect_uri)
        data = {
            "client_id": self.__client_id,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "code_verifier": code_verifier
        }

        res = requests.post(SpotifyApi.TOKEN_ENDPOINT, data=data, headers=headers)
        pprint(res.json())
        if res.status_code!=200: return None
        data = res.json()
        return data

    def init_sp_client(self, token):
        self.token = token
        self.spotify_client = Spotify(auth=token)

    @renew_token_if_needed
    def info_usuario(self):
        return self.spotify_client.current_user()
    
    @renew_token_if_needed
    def buscar_cancion(self, nombre):
        return self.spotify_client.search(nombre, limit=10)

    @renew_token_if_needed
    def user_top_tracks(self, top):
        top_tracks = self.spotify_client.current_user_top_tracks(time_range='short_term', limit=top)
        return [
            {
                "id": item["id"], 
                "title": item['name'],
                "artist_name": item['artists'][0]['name'],
                "uri": item["uri"],
                "img": item["album"]["images"][1]["url"],
            } 
            for item in top_tracks['items']
        ]
    
    @renew_token_if_needed
    def obtener_cancion(self, id):
        return self.spotify_client.track(id)

    @renew_token_if_needed
    def obtener_info_canciones(self, q:list):
        return self.spotify_client.tracks(q)

    @renew_token_if_needed
    def obtener_artistas(self):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        res = requests.get(f"https://api.spotify.com/v1/recommendations?limit=8&seed_genres=anime,pop,raggeton,j-pop", headers=headers)
        # &seed_tracks=0c6xIDDpzE81m2q797ordA

        if res.status_code == 200:
            artistas = res.json()
            info_artistas = []

            for data in artistas["tracks"]:
                images = data.get("album",{}).get("images", [{}])
                img = list(filter(lambda img: img["height"] >= 300, images))[0]

                data_artista = data["artists"]
                info_artistas+= [{"id":artista["id"], "name": artista["name"], "link":artista["external_urls"]["spotify"], "img":img.get("url", "")} for artista in data_artista]

            return info_artistas
        else:
            print("Error al obtener los artistas:", res.text, res.status_code)
            return []