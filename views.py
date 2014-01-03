import webapp2
import jinja2

from google.appengine.api import users
from google.appengine.ext import ndb

from models import Album, Photo

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates')
)


class BaseHandler(webapp2.RequestHandler):

    def render_template(self, template_name, template_values={}):
        template = env.get_template(template_name)
        self.response.write(template.render(template_values))


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

        # TODO: In the future redirect to the album page
        self.redirect('/')