import webapp2
import jinja2

from google.appengine.api import users
from google.appengine.ext import ndb

from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.blobstore import blobstore

from models import Album, Photo

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates')
)


class BaseHandler(webapp2.RequestHandler):

    def render_template(self, template_name, template_values={}):
        template = env.get_template(template_name)
        self.response.write(template.render(template_values))

    def raise_404(self):
        self.error(404)
        self.render_template('404_notfound.html')


class MainHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        login_url = users.create_login_url(self.request.uri)
        logout_url = users.create_logout_url(self.request.uri)

        if user:
            query = Album.query(
                ancestor=ndb.Key('User', user.email())
            ).order(-Album.date_created)
            albums = query.fetch(10)
        else:
            albums = []

        template_values = {
            'user': user,
            'login_url': login_url,
            'logout_url': logout_url,
            'albums': albums,
        }

        self.render_template('index.html', template_values)


class CreateAlbumHandler(BaseHandler):
    def get(self):
        self.render_template('create_album.html')

    def post(self):
        user = users.get_current_user()

        album = Album(parent=ndb.Key('User', user.email()))
        album.name = self.request.get('album_name')
        album.description = self.request.get('album_desc')

        album.put()

        self.redirect('/album/%s/view' % album.key.integer_id())


class ViewAlbumHandler(BaseHandler):
    def get(self, album_id):
        user = users.get_current_user()
        album = Album.get_by_id(
            int(album_id),
            parent=ndb.Key('User', user.email())
        )

        if album:
            photo_query = Photo.query(
                ancestor=album.key
            ).order(Photo.date_created)

            template_values = {
                'user': user,
                'album': album,
                'photos': photo_query.fetch(None),
            }

            self.render_template('view_album.html', template_values)
        else:
            self.raise_404()


class AddPhotoHandler(BaseHandler):
    def get(self, album_id):
        user = users.get_current_user()
        album = Album.get_by_id(
            int(album_id),
            parent=ndb.Key('User', user.email())
        )
        upload_url = blobstore.create_upload_url(
            '/album/%s/upload-photo' % album.key.integer_id()
        )

        template_values = {
            'user': user,
            'album': album,
            'upload_url': upload_url,
        }

        self.render_template('add_photo.html', template_values)


class UploadPhotoHandler(blobstore_handlers.BlobstoreUploadHandler):

    def post(self, album_id):
        uploaded_files = self.get_uploads('photo')

        user = users.get_current_user()
        album = Album.get_by_id(
            int(album_id),
            parent=ndb.Key('User', user.email())
        )

        photo = Photo(parent=album.key)
        photo.name = self.request.get('photo_name')
        photo.blob_info_key = uploaded_files[0].key()

        photo.put()

        self.redirect('/album/%s/view' % album.key.integer_id())


class DownloadPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):

    def get(self, album_id, photo_id):
        user = users.get_current_user()
        album = Album.get_by_id(
            int(album_id),
            parent=ndb.Key('User', user.email())
        )
        photo = Photo.get_by_id(
            int(photo_id),
            parent=album.key
        )

        self.send_blob(blobstore.BlobInfo.get(photo.blob_info_key))