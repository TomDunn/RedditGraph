import praw

r = praw.Reddit(user_agent='subreddit info grabber 1.0 by u/lungfungus')
r.config.log_requests = 2
