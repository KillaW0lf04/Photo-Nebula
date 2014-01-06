from views import *
from photos import *


app = webapp2.WSGIApplication([
    (r'/', MainHandler),
    (r'/album/create', CreateAlbumHandler),
    (r'/album/(\d+)/view', ViewAlbumHandler),
    (r'/album/(\d+)/edit', EditAlbumHandler),
    (r'/album/(\d+)/add-photo', AddPhotoHandler),
    (r'/album/(\d+)/delete', DeleteAlbumHandler),
    (r'/album/(\d+)/upload-photo', UploadPhotoHandler),
    (r'/album/(\d+)/photo/(\d+)', DownloadPhotoHandler),
    (r'/album/(\d+)/add-comment', AddAlbumCommentHandler),
    (r'/album/(\d+)/photo/(\d+)/view', ViewPhotoHandler),
    (r'/album/(\d+)/photo/(\d+)/delete', DeletePhotoHandler),
    (r'/album/(\d+)/photo/(\d+)/add-comment', AddPhotoCommentHandler),
    (r'/about', AboutHandler),
], debug=True)
