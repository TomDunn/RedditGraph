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
        (   '<YOUR CONSUMER KEY>',
            '<YOUR CONSUMER SECRET>',
            '<YOUR ACCESS TOKEN KEY>',
            '<YOUR ACCESS TOKEN SECRET>'
        )
    )
