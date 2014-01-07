from utils import DEFAULT_DOMAIN_KEY, get_user
from models import Album, Photo

from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.blobstore import blobstore

from google.appengine.api import images


def delete_photo(photo):
    # Delete data
    blobstore.BlobInfo.get(photo.blob_info_key).delete()
    photo.key.delete()


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
            self.response.write('You must be signed in with your google account to upload photos')


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

        # All possible options
        height = self.request.get('height')
        width = self.request.get('width')
        rotate = self.request.get('rotate')
        lucky = self.request.get('lucky')
        hflip = self.request.get('hflip')

        if height or width or rotate:
            try:
                img = images.Image(blob_key=photo.blob_info_key)

                height = None if not height else int(height)
                width = None if not width else int(width)
                rotate = None if not rotate else int(rotate)
                lucky = None if not lucky else bool(lucky)
                hflip = None if not hflip else bool(hflip)

                if width and height:
                    # Resizing always preserves aspect ratio
                    img.resize(height=height, width=width)
                elif width:
                    img.resize(width=width)
                elif height:
                    img.resize(height=height)

                if rotate:
                    img.rotate(rotate)

                if hflip:
                    img.horizontal_flip()

                if lucky:
                    img.im_feeling_lucky()

                img = img.execute_transforms(output_encoding=images.PNG)

                self.response.headers['Content-Type'] = 'image/png'
                self.response.write(img)
            except Exception as e:
                self.response.write('Unable to process request: %s' % e.message)
        else:
            self.send_blob(blobstore.BlobInfo.get(photo.blob_info_key))
