from collections import namedtuple
import time

class Util():

    @staticmethod
    def add_and_refresh(session, obj):
        session.add(obj)
        session.flush()
        session.refresh(obj)

    @staticmethod
    def get_or_create(cls, session, reddit_id):
        thing = session.query(cls).filter(cls.reddit_id == reddit_id).first()

        if (thing == None):
            thing = cls.create(session, reddit_id)

        return thing

    @staticmethod
    def now():
        return time.time()

    @staticmethod
    def plain_id(reddit_id):
        if '_' in reddit_id:
            return reddit_id.split('_')[1]

        return reddit_id

    @staticmethod
    def update_user(cls, obj, session, username):
        user = cls.get_or_create(session, username)
        obj.author_id = user.id

    @staticmethod
    def update_subreddit(cls, obj, session, display_name):
        sub = cls.get_or_create(session, display_name)
        obj.subreddit_id = sub.id

    @staticmethod
    def patch_author(author):
        if author is None:
            return '[deleted]'

        if type(author) in [str, unicode]:
            return author

        return author.name

    @staticmethod
    def is_400_exception(e):
        e = str(e)
        return '403' in e or '404' in e

    @staticmethod
    def is_500_exception(e):
        e = str(e)
        return '500' in e
