from mongoengine import StringField, Document

class Usuario(Document):
    username = StringField(required=True)
    spotify_id = StringField(required=True, unique=True)
    uri = StringField(required=True)
    img = StringField(required=False)
