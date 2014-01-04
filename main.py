from views import *

app = webapp2.WSGIApplication([
    (r'/', MainHandler),
    (r'/album/create', CreateAlbumHandler),
    (r'/album/(\d+)/view', ViewAlbumHandler),
    (r'/album/(\d+)/add-photo', AddPhotoHandler),
    (r'/album/(\d+)/upload-photo', UploadPhotoHandler),
    (r'/album/(\d+)/photo/(\d+)', DownloadPhotoHandler),
    (r'/album/(\d+)/add-comment', AddCommentHandler),
    (r'/album/(\d+)/photo/(\d+)/view', ViewPhotoHandler),
], debug=True)
