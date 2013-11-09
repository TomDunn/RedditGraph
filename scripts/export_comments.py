import csv
from BeautifulSoup import BeautifulSoup
from HTMLParser import HTMLParser

from snudown import markdown

from db import Session
from models.Comment import Comment
from models.Subreddit import Subreddit

def normalize_markdown_text(parser, source):
    rendered  = markdown(unicode(source).encode('utf-8'))
    html_body = ' '.join(rendered.splitlines())
    soup      = BeautifulSoup(html_body)
    text      = ' '.join(soup.findAll(text=True))
    text      = parser.unescape(text)
    return unicode(' '.join(text.splitlines()).replace(',', ' ')).encode('utf-8')


session = Session()
parser = HTMLParser()
subreddit_ids = set()
count = 0

with open('data/Comments.csv', 'wb') as f:
    writer = csv.writer(f, delimiter=',', quotechar='|')

    for comment in session.query(Comment):
        if comment.body is None or len(comment.body) < 1:
            continue

        if comment.post is None or comment.post.subreddit_id is None:
            continue

        count += 1

        body = normalize_markdown_text(parser, comment.body)
        subreddit_ids.add(comment.post.subreddit_id)

        writer.writerow([comment.post.subreddit_id, body])

    for subreddit_id in subreddit_ids:
        subreddit = session.query(Subreddit).filter(Subreddit.id == subreddit_id).one()

        if subreddit.description is None or len(subreddit.description) < 1:
            continue

        count += 1

        description = normalize_markdown_text(parser, subreddit.description)
        writer.writerow([subreddit.id, description])

print "number of lines:", count
print "number of subs:", len(subreddit_ids)
