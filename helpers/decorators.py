import praw

from helpers.ExponentialBackoff import ExponentialBackoff
from models.Util import Util

def praw_retry_http500(fn):

    backoff = ExponentialBackoff()

    def wrapped(**kwargs):
        while True:
            try:
                return fn(**kwargs)
            except praw.requests.HTTPError as e:
                if Util.is_500_exception(e):
                    backoff()
                else:
                    raise e

    return wrapped