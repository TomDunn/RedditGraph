from db import Session
from models.Comment import Comment
from models.Post import Post
from models.User import User
from models.Util import Util
from helpers.RFactory import r

def main(notify):
    session = Session()
    gen     = r.get_comments('all', limit=10000)
    count   = session.query(Comment).count()

    notify("Starting w/ %d" % count)

    for praw_comment in gen:
        count += 1

        comment = Comment.get_or_create(session, praw_comment.id)
        comment.update_from_praw(praw_comment)

        author_name = Util.patch_author(praw_comment.author)
        user = User.get_or_create(session, author_name)
        post = Post.get_or_create(session, praw_comment.link_id)

        comment.author_id   = user.id
        comment.post_id     = post.id

        session.add(comment)
        session.commit()

    notify("Ending w/ %d" % count)
