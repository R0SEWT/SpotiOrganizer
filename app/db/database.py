import mongoengine as db
from os import getenv

# Conexión a MongoDB
def create_conetion_db():
    db.connect(db=getenv("DB_NAME"), host=getenv("URI_DB"))