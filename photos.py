from main import DEFAULT_DOMAIN_KEY, get_user
from models import Album, Photo

from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.blobstore import blobstore

from google.appengine.api import images


class UploadPhotoHandler(blobstore_handlers.BlobstoreUploadHandler):

    def post(self, album_id):
        uploaded_files = self.get_uploads('photo')

        user = get_user()

        if user:
            album = Album.get_by_id(
                int(album_id),
                parent=DEFAULT_DOMAIN_KEY
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
            parent=DEFAULT_DOMAIN_KEY
        )
        photo = Photo.get_by_id(
            int(photo_id),
            parent=album.key
        )

        height = self.request.get('height')

        if height:
            img = images.Image(blob_key=photo.blob_info_key)
            img.resize(height=int(height))
            img = img.execute_transforms(output_encoding=images.PNG)

            self.response.headers['Content-Type'] = 'image/png'
            self.response.write(img)
        else:
            self.send_blob(blobstore.BlobInfo.get(photo.blob_info_key))
