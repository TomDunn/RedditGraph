from db import Session
from models.Comment import Comment
from models.Post import Post
from helpers.RFactory import r

def main(notify):
    session = Session()
    gen     = r.get_comments('all', limit=1000)
    count   = session.query(Comment).count()

    notify("Starting w/ %d" % count)

    for comment in gen:
        count += 1

        c = Comment()
        c.update_from_praw(comment)

        c = session.merge(c)
        session.add(c)

        if (count % 20 == 0):
            session.commit()

    session.commit()
    notify("Ending w/ %d" % count)
