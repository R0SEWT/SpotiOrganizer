from flask import Blueprint, render_template, current_app, session, request, redirect
from ..spotify import SpotifyApi
from .controlador import AuthCtrl
from ..decorators import no_login_required

auth_routes = Blueprint('auth', __name__)

@auth_routes.get("/login")
@no_login_required
def html_login():
    return render_template("login.html")

@auth_routes.get("/login-spotify")
@no_login_required
def login():
    spotify_client:SpotifyApi = current_app.config.get("spotify_client")
    res = {"url": spotify_client.get_url_oauth()}
    print(res)
    return res

@auth_routes.post("/logining")
@no_login_required
def callback():
    spotify_client:SpotifyApi = current_app.config.get("spotify_client")
    spotify_client.redirect_uri = (request.host_url + "login").replace("http://", "https://")

    data:dict = request.json
    code = data.get("code")
    codeVerifier = data.get("codeVerifier")

    data_token = spotify_client.obtener_token(code, codeVerifier)
    if not data_token:
        return {"status": False}
    
    token = data_token["access_token"]
    refresh_token = data_token["refresh_token"]
    
    spotify_client.refresh_token = refresh_token
    spotify_client.init_sp_client(token)

    current_user = spotify_client.info_usuario()
    username, id, uri = current_user["display_name"], current_user["id"], current_user["uri"]
    img = ""
    
    if images:=current_user["images"]:
        img = images[0]["url"]

    AuthCtrl.login(username, id, uri, img)

    session["user"] = {
        "username": username,
        "id": id,
        "uri": uri,
        "img": img,
        "token": token
    }
    return {"status": True}

@auth_routes.get("/logout")
def logout():
    del session["user"]
    return redirect("/")