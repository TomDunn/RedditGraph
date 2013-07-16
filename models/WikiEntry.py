from sqlalchemy import Column, Integer, String, ForeignKey
from db import Base

class WikiEntry(Base):
    __tablename__ = 'wiki_entries'
    id              = Column(Integer, primary_key = True)
    subreddit_id    = Column(String, ForeignKey('subreddits.id'))
    content_html    = Column(String)
    page            = Column(String)

    def update_from_praw(self, p):
        self.subreddit_id = p.subreddit.id
        self.content_html = p.content_html
        self.page         = p.page
