from models import User

from google.appengine.ext import ndb
from google.appengine.api import users

DEFAULT_DOMAIN_KEY = ndb.Key('Domain', 'default')


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
            user = User(parent=ndb.Key('Domain', DEFAULT_DOMAIN_KEY))
            user.nickname = google_user.nickname()
            user.email = google_user.email()

            user.put()
        else:
            user = user_results[0]

        return user
    else:
        return None
