from mongoengine import Document, ObjectIdField, StringField, ListField

class Playlist(Document):
    user_id = ObjectIdField(required=True)
    name = StringField(required=True)
    description = StringField()
    songs = ListField(ObjectIdField())