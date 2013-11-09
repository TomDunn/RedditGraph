from models.UserVoteBasedPostSimilarities import UserVoteBasedPostSimilarities as UVBPS
from db import Session

session = Session()

session.query(UVBPS).delete()
session.commit()

with open('data/UserPostVoteCorr.csv', 'rb') as f:
    for line in f:
        p1, p2, corr, intersect = line.split(';')

        sim = UVBPS()

        sim.post_id1 = p1
        sim.post_id2 = p2
        sim.similarity = corr
        sim.intersect = intersect

        session.add(sim)

session.commit()
