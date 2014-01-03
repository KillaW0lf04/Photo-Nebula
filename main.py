import webapp2
from views import MainHandler, CreateAlbumHandler

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/album/create', CreateAlbumHandler),
], debug=True)
