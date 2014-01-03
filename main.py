import webapp2
from views import MainHandler, CreateAlbumHandler, ViewAlbumHandler

app = webapp2.WSGIApplication([
    (r'/', MainHandler),
    (r'/album/create', CreateAlbumHandler),
    (r'/album/view/(\d+)', ViewAlbumHandler),
], debug=True)
