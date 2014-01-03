from google.appengine.ext import ndb


class Photo(ndb.Model):
    name = ndb.StringProperty()
    blob_info_key = ndb.BlobKeyProperty()


class Album(ndb.Model):
    name = ndb.StringProperty()
    description = ndb.StringProperty()
    date_created = ndb.DateTimeProperty(auto_now_add=True)
