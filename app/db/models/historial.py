from mongoengine import Document, ObjectIdField, StringField, DateTimeField, ListField
from datetime import datetime

class Historial(Document):
    user_id = ObjectIdField(required=True)
    song_id = StringField(required=True)
    played_at = DateTimeField(default=datetime.utcnow)