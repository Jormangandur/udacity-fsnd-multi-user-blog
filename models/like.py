from google.appengine.ext import db
from helpers import *


class Like(db.Model):
    post_id = db.IntegerProperty(required=True)
    liked_by_id = db.IntegerProperty()
