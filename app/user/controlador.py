from ..db import Historial, Favoritos, Usuario

class UserCtrl:
    @classmethod
    def agregar_al_historial(cls, user_id, song_id):
        Historial(user_id=user_id, song_id=song_id).save()
    
    @classmethod
    def agregar_favoritos(cls, user_id, song_id):
        if not Favoritos.objects(user_id=user_id, song_id=song_id):
            Favoritos(user_id=user_id, song_id=song_id).save()
        else:
            Favoritos.objects(user_id=user_id, song_id=song_id).delete()

    @classmethod
    def obtener_historial(cls, user_id, page:int):
        items_per_page = 15
        offset = (page - 1) * items_per_page
        return Historial.objects(user_id=user_id).skip(offset).limit(items_per_page)
    
    @classmethod
    def obtener_favoritos(cls, user_id):
        return Favoritos.objects(user_id=user_id)
    
    @classmethod
    def obtener_usuarios(cls):
        return Usuario.objects()