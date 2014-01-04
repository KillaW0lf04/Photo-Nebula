import webapp2
import jinja2

from google.appengine.api import users
from google.appengine.ext import ndb

from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.blobstore import blobstore

from models import Album, Photo, Comment, User

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates')
)

DEFAULT_DOMAIN = 'default'


def get_user():
    """
    Checks if the user has signed in with his/her google account before. If not
    a new User is created.
    """
    google_user = users.get_current_user()

    if google_user:
        user_query = User.query(
            User.email == google_user.email()
        )
        user_results = user_query.fetch(1)

        if not user_results:
            user = User(parent=ndb.Key('Domain', DEFAULT_DOMAIN))
            user.nickname = google_user.nickname()
            user.email = google_user.email()

            user.put()
        else:
            user = user_results[0]

        return user
    else:
        return None


class BaseHandler(webapp2.RequestHandler):

    def render_template(self, template_name, template_values={}):
        template = env.get_template(template_name)
        self.response.write(template.render(template_values))

    def raise_error(self, error):
        if error == 404:
            message = 'The specified page was not found'
        elif error == 500:
            message = 'Internal Server Error'
        else:
            message = 'An unknown error occurred!'

        template_values = {
            'error_number': error,
            'error_message': message,
        }

        self.error(error)
        self.render_template('http_error.html', template_values)


class MainHandler(BaseHandler):
    def get(self):
        user = get_user()
        login_url = users.create_login_url(self.request.uri)
        logout_url = users.create_logout_url(self.request.uri)

        query = Album.query().order(-Album.date_created)
        albums = query.fetch(10)

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
        user = get_user()

        album = Album(parent=ndb.Key('Domain', DEFAULT_DOMAIN))
        album.author = user.key
        album.name = self.request.get('album_name')
        album.description = self.request.get('album_desc')

        album.put()

        self.redirect('/album/%s/view' % album.key.integer_id())


class ViewAlbumHandler(BaseHandler):
    def get(self, album_id):
        user = get_user()
        album = Album.get_by_id(
            int(album_id),
            ndb.Key('Domain', DEFAULT_DOMAIN)
        )

        if album:
            photo_query = Photo.query(
                ancestor=album.key
            )

            comments_query = Comment.query(
                ancestor=album.key
            ).order(-Comment.date_created)

            template_values = {
                'user': user,
                'album': album,
                'photos': photo_query.fetch(None),
                'comments': comments_query.fetch(None),
            }

            self.render_template('view_album.html', template_values)
        else:
            self.raise_error(404)


class AddPhotoHandler(BaseHandler):
    def get(self, album_id):
        user = get_user()
        album = Album.get_by_id(
            int(album_id),
            parent=ndb.Key('Domain', DEFAULT_DOMAIN)
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

        user = get_user()
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


class DownloadPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):

    def get(self, album_id, photo_id):
        user = get_user()
        album = Album.get_by_id(
            int(album_id),
            parent=ndb.Key('Domain', DEFAULT_DOMAIN)
        )
        photo = Photo.get_by_id(
            int(photo_id),
            parent=album.key
        )

        self.send_blob(blobstore.BlobInfo.get(photo.blob_info_key))


class AddCommentHandler(BaseHandler):

    def get(self, album_id):
        self.raise_error(404)

    def post(self, album_id):
        user = get_user()
        album = Album.get_by_id(
            int(album_id),
            parent=ndb.Key('User', user.email)
        )

        comment = Comment(parent=album.key)
        comment.text = self.request.get('comment_text')
        comment.author = user.key

        comment.put()

        self.redirect('/album/%s/view' % album.key.integer_id())


class ViewPhotoHandler(BaseHandler):

    def get(self, album_id, photo_id):
        user = get_user()
        album = Album.get_by_id(
            int(album_id),
            parent=ndb.Key('Domain', DEFAULT_DOMAIN)
        )
        photo = Photo.get_by_id(
            int(photo_id),
            parent=album.key
        )

        image_url = '%s/album/%s/photo/%s' % (self.request.host_url, album.key.integer_id(), photo.key.integer_id())

        comments_query = Comment.query(
            ancestor=album.key
        ).order(-Comment.date_created)

        comments = comments_query.fetch(None)

        template_values = {
            'image_url': image_url,
            'photo': photo,
            'album': album,
            'comments': comments,
        }

        self.render_template('view_photo.html', template_values)
