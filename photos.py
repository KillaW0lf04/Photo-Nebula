from main import DEFAULT_DOMAIN, get_user
from models import Album, Photo

from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.blobstore import blobstore


class UploadPhotoHandler(blobstore_handlers.BlobstoreUploadHandler):

    def post(self, album_id):
        uploaded_files = self.get_uploads('photo')

        user = get_user()

        if user:
            album = Album.get_by_id(
                int(album_id),
                parent=ndb.Key('Domain', DEFAULT_DOMAIN)
            )

            photo = Photo(parent=album.key)
            photo.author = user.key
            photo.name = self.request.get('photo_name')
            photo.blob_info_key = uploaded_files[0].key()

            photo.put()

            self.redirect('/album/%s/view' % album.key.integer_id())
        else:
            self.response.write('UNKNOWN SERVER ERROR')


class DownloadPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):

    def get(self, album_id, photo_id):
        album = Album.get_by_id(
            int(album_id),
            parent=ndb.Key('Domain', DEFAULT_DOMAIN)
        )
        photo = Photo.get_by_id(
            int(photo_id),
            parent=album.key
        )

        self.send_blob(blobstore.BlobInfo.get(photo.blob_info_key))
