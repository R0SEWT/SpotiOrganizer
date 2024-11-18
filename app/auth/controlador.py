from ..db import Usuario

class AuthCtrl:
    @classmethod
    def login(cls, username, spotify_id, uri, img):
        if not Usuario.objects(spotify_id=spotify_id):
            Usuario(username=username, spotify_id=spotify_id, uri=uri, img=img).save()