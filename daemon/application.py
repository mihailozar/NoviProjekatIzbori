from redis import Redis
from configuration import Configuration
from models import database,Votes,Elections,Participants,Resaults
from sqlalchemy import and_,create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask
from dateutil import parser

import datetime

engine = create_engine(Configuration.SQLALCHEMY_DATABASE_URI, echo=False)
Session = sessionmaker(bind=engine)
session = Session()


while True:
    try:
        with Redis(host=Configuration.REDIS_HOST) as redis:
            if len(redis.lrange(Configuration.REDIS_VOTES,0,-1))!=0:
                row=redis.lpop(Configuration.REDIS_VOTES)
                row=row.decode("utf-8")
                row=row.split(", ")
                # now=datetime.datetime.now().replace(microsecond=0)
                now=parser.parse( row[3])
                print(now,flush=True)

                election=session.query(Elections).filter(and_(
                    Elections.start<=now,
                    Elections.end>=now
                )).first()
                session.commit()

                if election!=None:

                    isDuplicate=session.query(Votes).filter(and_(Votes.guid==row[0],Votes.isValid==None,Votes.idElection==election.id)).first()
                    session.commit()
                    if isDuplicate!=None:
                        print("stavlja duplikat", flush=True)
                        vote=Votes(guid=row[0],jmbg=str(row[2]),idElection=election.id,pollNumber=row[1],isValid="Duplicate ballot.")
                        session.add(vote)
                        session.commit()
                    elif session.query(Resaults).filter(and_(Resaults.idElection==election.id ,Resaults.participantNumber==row[1]))\
                            .first()==None:
                        print("stavlja los", flush=True)
                        vote=Votes(guid=row[0],jmbg=str(row[2]),idElection=election.id,pollNumber=row[1],isValid="Invalid poll number.")
                        session.add(vote)
                        session.commit()
                    else:
                        print("stavlja dobar", flush=True)
                        vote = Votes(guid=row[0], jmbg=str(row[2]), idElection=election.id, pollNumber=row[1])
                        session.add(vote)
                        session.commit()


                # else:
                    # raise Exception("There isn't active election")
                session.commit()
            # else:
            #     raise Exception("Nema vise u redu")

    except Exception as excep:
        print(excep,flush=True)
