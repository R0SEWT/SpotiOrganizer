from mongoengine import Document, StringField

class Favoritos(Document):
    user_id = StringField(required=True)
    song_id = StringField(required=True)