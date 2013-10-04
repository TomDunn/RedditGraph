import time

from pydispatch import dispatcher
from sqlalchemy import Column, Integer, String, Float, ForeignKey, event
from sqlalchemy.orm import relationship, backref, object_session
from sqlalchemy.schema import Sequence

from db import Base
from models.User import User

class UserLock(Base):
    __tablename__ = 'user_locks'

    id = Column(Integer, Sequence('users_locks_seq'), primary_key=True)

    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    user    = relationship('User', backref=backref('lock', uselist=False))

    STATUS_DONE = 'DONE'
    STATUS_WIP  = 'WIP'
    STATUS_NONE = 'NONE'

    status      = Column(String, default=STATUS_NONE)
    locker      = Column(String)
    locked_at   = Column(Float, default=0.0)

    @classmethod
    def create(cls, session, user_id):
        lock = cls()
        lock.user_id = user_id
        session.add(lock)

        return lock

    @classmethod
    def lock(cls, session, worker_id, n=10):
        now = time.mktime(time.gmtime())
        sq = session.query(UserLock.id).join(User) \
            .filter(User.reddit_id == None, UserLock.status == UserLock.STATUS_NONE) \
            .limit(n).subquery()

        return session.query(UserLock).filter(UserLock.id.in_(sq)) \
            .update({'status': UserLock.STATUS_WIP, 'locker': worker_id, 'locked_at': now}, synchronize_session='fetch')

    @classmethod
    def get_locked(cls, session, worker_id, status=None):

        if status == None:
            status = UserLock.STATUS_WIP

        return session.query(cls).filter(cls.locker == worker_id, cls.status == status)

def create_user_lock(sender):
    session = object_session(sender)
    UserLock.create(session, sender.id)
    session.commit()

dispatcher.connect(create_user_lock, signal=User.CREATED_SIGNAL, sender=dispatcher.Any)
