import webapp2
import jinja2

from google.appengine.api import users
from google.appengine.ext.blobstore import blobstore

from models import Album, Photo, Comment
from utils import get_user, DEFAULT_DOMAIN_KEY
from photos import delete_photo


env = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates')
)


def get_covered_albums(query, fetch=None):
    albums = query.fetch(fetch)

    for album in albums:
        photos = Photo.query(
            ancestor=album.key
        ).order(-Photo.date_created).fetch(1)

        if photos:
            album.cover = photos[0].key
        else:
            album.cover = None

    return albums


class BaseHandler(webapp2.RequestHandler):

    def redirect_to_login(self):
        login_url = users.create_login_url(self.request.uri)
        self.redirect(login_url)

    def render_template(self, template_name, template_values={}):
        template = env.get_template(template_name)

        # Values expected by base
        template_values['user'] = get_user()
        template_values['login_url'] = users.create_login_url(self.request.uri)
        template_values['logout_url'] = users.create_logout_url(self.request.uri)

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
        query = Album.query().order(-Album.date_created)

        albums = get_covered_albums(query, 3)

        template_values = {
            'albums': albums,
        }

        self.render_template('index.html', template_values)


class CreateAlbumHandler(BaseHandler):
    def get(self):
        if get_user():
            self.render_template('create_album.html')
        else:
            self.redirect_to_login()

    def post(self):
        user = get_user()

        if user:
            album = Album(parent=DEFAULT_DOMAIN_KEY)
            album.author = user.key
            album.name = self.request.get('album_name')
            album.description = self.request.get('album_desc')

            album.put()

            self.redirect('/album/%s/view' % album.key.integer_id())
        else:
            self.redirect_to_login()


class ViewAlbumHandler(BaseHandler):
    def get(self, album_id):
        user = get_user()
        album = Album.get_by_id(
            int(album_id),
            DEFAULT_DOMAIN_KEY
        )

        if album:
            upload_url = blobstore.create_upload_url('/album/%s/upload-photo' % album_id)

            photo_query = Photo.query(
                ancestor=album.key
            )

            comments_query = Comment.query(
                Comment.parent == album.key
            ).order(-Comment.date_created)

            template_values = {
                'user': user,
                'album': album,
                'photos': photo_query.fetch(None),
                'comments': comments_query.fetch(None),
                'upload_url': upload_url,
            }

            self.render_template('view_album.html', template_values)
        else:
            self.raise_error(404)


class AddPhotoHandler(BaseHandler):
    def get(self, album_id):
        user = get_user()

        if user:
            album = Album.get_by_id(
                int(album_id),
                parent=DEFAULT_DOMAIN_KEY
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
        else:
            self.redirect_to_login()


class AddAlbumCommentHandler(BaseHandler):

    def get(self, album_id):
        self.raise_error(404)

    def post(self, album_id):
        user = get_user()

        if user:
            album = Album.get_by_id(
                int(album_id),
                parent=DEFAULT_DOMAIN_KEY
            )

            comment = Comment(parent=album.key)
            comment.text = self.request.get('comment_text')
            comment.author = user.key
            comment.parent = album.key

            comment.put()

            self.redirect('/album/%s/view' % album.key.integer_id())
        else:
            self.redirect_to_login()


class AddPhotoCommentHandler(BaseHandler):

    def get(self, album_id, photo_id):
        self.raise_error(404)

    def post(self, album_id, photo_id):
        user = get_user()

        if user:
            album = Album.get_by_id(
                int(album_id),
                parent=DEFAULT_DOMAIN_KEY
            )
            photo = Photo.get_by_id(
                int(photo_id),
                parent=album.key
            )

            comment = Comment(parent=photo.key)
            comment.text = self.request.get('comment_text')
            comment.author = user.key
            comment.parent = photo.key

            comment.put()

            self.redirect('/album/%s/photo/%s/view' % (album_id, photo_id))
        else:
            self.redirect_to_login()


class ViewPhotoHandler(BaseHandler):

    def get(self, album_id, photo_id):
        album = Album.get_by_id(
            int(album_id),
            parent=DEFAULT_DOMAIN_KEY
        )
        photo = Photo.get_by_id(
            int(photo_id),
            parent=album.key
        )

        image_url = '%s/album/%s/photo/%s' % (
            self.request.host_url,
            album.key.integer_id(),
            photo.key.integer_id()
        )

        comments_query = Comment.query(
            Comment.parent == photo.key
        ).order(-Comment.date_created)

        comments = comments_query.fetch(None)

        template_values = {
            'image_url': image_url,
            'photo': photo,
            'album': album,
            'comments': comments,
        }

        self.render_template('view_photo.html', template_values)


class DeleteAlbumHandler(BaseHandler):

    def post(self, album_id):
        album = Album.get_by_id(
            int(album_id),
            parent=DEFAULT_DOMAIN_KEY
        )

        if album.author == get_user().key:
            photos_query = Photo.query(
                ancestor=album.key
            )

            photos = photos_query.fetch(None)
            for photo in photos:
                delete_photo(photo)

            album.key.delete()

            self.redirect('/')
        else:
            self.raise_error(500)


class DeletePhotoHandler(BaseHandler):

    def post(self, album_id, photo_id):
        album = Album.get_by_id(
            int(album_id),
            parent=DEFAULT_DOMAIN_KEY
        )
        photo = Photo.get_by_id(
            int(photo_id),
            parent=album.key
        )

        if photo.author == get_user().key:
            delete_photo(photo)

            self.redirect('/album/%s/view' % album_id)
        else:
            self.raise_error('500')


class EditAlbumHandler(BaseHandler):

    def get(self, album_id):
        album = Album.get_by_id(
            int(album_id),
            parent=DEFAULT_DOMAIN_KEY
        )

        if get_user().key == album.author:
            self.render_template('edit_album.html', {'album': album})
        else:
            self.raise_error(500)

    def post(self, album_id):
        album = Album.get_by_id(
            int(album_id),
            parent=DEFAULT_DOMAIN_KEY
        )

        if get_user().key == album.author:
            album.name = self.request.get('album_name')
            album.description = self.request.get('album_desc')
            album.put()

            self.redirect('/album/%s/view' % album_id)
        else:
            self.raise_error(500)


class EditPhotoHandler(BaseHandler):

    def get(self, album_id, photo_id):
        album = Album.get_by_id(
            int(album_id),
            parent=DEFAULT_DOMAIN_KEY
        )
        photo = Photo.get_by_id(
            int(photo_id),
            parent=album.key
        )

        if photo.author == get_user().key:
            template_values = {
                'album': album,
                'photo': photo,
            }

            self.render_template('edit_photo.html', template_values)
        else:
            self.raise_error(500)

    def post(self, album_id, photo_id):
        album = Album.get_by_id(
            int(album_id),
            parent=DEFAULT_DOMAIN_KEY
        )
        photo = Photo.get_by_id(
            int(photo_id),
            parent=album.key
        )

        if photo.author == get_user().key:
            photo.name = self.request.get('photo_name')
            photo.put()

            self.redirect('/album/%s/photo/%s/view' % (album_id, photo_id))
        else:
            self.raise_error(500)


class SearchHandler(BaseHandler):

    def post(self):
        q = self.request.get('search_text')

        self.redirect('/browse?q=%s' % q)


class BrowseAlbumsHandler(BaseHandler):

    def get(self):
        query = Album.query(
            ancestor=DEFAULT_DOMAIN_KEY
        ).order(-Album.date_created)

        albums = get_covered_albums(query)

        template_values = {
            'albums': albums
        }

        self.render_template('browse_albums.html', template_values)


class AboutHandler(BaseHandler):

    def get(self):
        self.render_template("about.html")


class DeleteAlbumCommentHandler(BaseHandler):

    def get(self, album_id, comment_id):
        album = Album.get_by_id(
            int(album_id),
            parent=DEFAULT_DOMAIN_KEY
        )

        comment = Comment.query(
            Comment.parent == album.key
        ).fetch(None)

        if get_user().key == comment[0].author:
            comment[0].key.delete()

            self.redirect('/album/%s/view' % album_id)
        else:
            self.raise_error(500)
