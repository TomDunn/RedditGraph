import argparse
import csv

from sqlalchemy.engine import reflection
from db import engine, Session

parser = argparse.ArgumentParser()
parser.add_argument('model_class', help='a model class to export')
args = parser.parse_args()

module = __import__('models.' + args.model_class)
module =  getattr(module, args.model_class)
cls    =  getattr(module, args.model_class)
inspector = reflection.Inspector.from_engine(engine)

columns = [col['name'] for col in inspector.get_columns(cls.__tablename__)]

session = Session()
file_name = 'data/' + args.model_class + '.csv'

with open(file_name, 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='|')

    for row in session.query(cls):
        tmp = dict()

        for col in columns:
            tmp[col] = row.__dict__[col]

            typ = type(tmp[col])

            if typ == str or typ == unicode:
                tmp[col] = ' '.join(tmp[col].splitlines())
                tmp[col] = unicode(tmp[col]).encode('utf-8')

        writer.writerow([tmp[col] for col in columns])

with open(file_name + 'schema', 'wb') as f:
    f.write(' '.join(columns))
