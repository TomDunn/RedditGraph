import time

from pydispatch import dispatcher
from sqlalchemy import Column, Integer, SmallInteger, ForeignKey
from sqlalchemy.orm import backref, object_session, relationship
from sqlalchemy.schema import Sequence

from db import Base
from models.User import User
from models.Util import Util

class UserMeta(Base):
    __tablename__ = 'users_meta'

    id = Column(Integer, Sequence('users_meta_seq'), primary_key=True)

    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    user    = relationship('User', backref=backref('meta', uselist=False))

    UNKNOWN = 0
    YES     = 1
    NO      = 2

    has_public_likes    = Column(SmallInteger, default=UNKNOWN)
    is_active           = Column(SmallInteger, default=UNKNOWN)

    @classmethod
    def create(cls, session, user_id):
        meta  = cls()
        meta.user_id = user_id

        Util.add_and_refresh(session, meta)
        return meta

def create_user_meta(sender):
    session = object_session(sender)
    UserMeta.create(session, sender.id)
    session.commit()

dispatcher.connect(create_user_meta, signal=User.CREATED_SIGNAL, sender=dispatcher.Any)
