from db import Session
from models.Post import Post
from models.User import User
from helpers.RFactory import r

session = Session()

for post in session.query(Post.author_id).distinct():
    user = User()
    user.id = post.author_id
    user = session.merge(user)

session.commit()
