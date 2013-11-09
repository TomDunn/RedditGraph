from os import environ
import twitter

"""
    Instantiate a twitter object with your:
        consumer_key,
        consumer_secret,
        access_token_key,
        access_token_secret

        See https://github.com/bear/python-twitter#using
"""
t = twitter.Twitter(
    auth=twitter.OAuth
        (   environ['TWITTER_CONSUMER_KEY'],
            environ['TWITTER_CONSUMER_SECRET'],
            environ['TWITTER_ACCESS_TOKEN_KEY'],
            environ['TWITTER_ACCESS_TOKEN_SECRET']
        )
    )
