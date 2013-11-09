from os import environ

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# different engines
engines = {
    'sqlite':          create_engine('sqlite:///db/db.sqlite', echo=False),
    'remote_postgres': create_engine(environ['REMOTE_POSTGRES_CONN'], echo=False),
    'local_postgres':  create_engine(environ['LOCAL_POSTGRES_CONN'], echo=False)
}

engine = engines[environ['REDDIT_USE_ENGINE']]

Session = sessionmaker(bind=engine)
Base = declarative_base()
