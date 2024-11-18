from flask import Blueprint, render_template, session, request, redirect
from .controlador import UserCtrl

user_routes = Blueprint('user', __name__)

@user_routes.before_request
def before_request():
    if 'user' not in session:
        if request.method == 'GET':
            return redirect('/login')
        return "No autenticado", 401

@user_routes.post("/agregar-favoritos")
def agregar_favoritos():
    data = request.json
    user_id = session["user"]["id"]
    song_id = data.get("id")
    
    try:
        UserCtrl.agregar_favoritos(user_id, song_id)
        return {"status": True}
    except Exception as e: 
        print(e)
        return { "status": False }

@user_routes.get("/favoritos")
def favoritos():
    return render_template("favoritos.html")

@user_routes.post("/agregar-historial")
def agregar_historial():
    data = request.json
    user_id = session["user"]["id"]
    song_id = data.get("id")

    try:
        UserCtrl.agregar_al_historial(user_id, song_id)
        return {"status": True}
    except: return { "status": False }

@user_routes.get("/historial")
def historial():
    args = request.args
    page = int(args.get("page", 1))
    user_id = session["user"]["id"]
    historial = UserCtrl.obtener_historial(user_id, page)
    
    return render_template("historial.html", historial=historial)

@user_routes.get("/obtener-historial")
def obtener_historial():
    args = request.args
    page = int(args.get("page", 1))
    user_id = session["user"]["id"]
    historial = UserCtrl.obtener_historial(user_id, page)

    return historial
