from flask_sqlalchemy import SQLAlchemy
from flask import jsonify

database=SQLAlchemy()

class Resaults(database.Model):
    __tablename__="resaults"

    id = database.Column(database.Integer, primary_key=True)
    idElection = database.Column(database.Integer, database.ForeignKey("elections.id"), nullable=False)
    idParticipants = database.Column(database.Integer, database.ForeignKey("participants.id"), nullable=False)
    participantNumber=database.Column(database.Integer,nullable=False)
    # numVotes = database.Column(database.Integer, nullable=False, default=0)
    #number all votes contains in elections


class Elections(database.Model):
    __tablename__="elections"

    id=database.Column(database.Integer, primary_key=True)
    start=database.Column(database.DateTime(timezone=True),nullable=False)
    end = database.Column(database.DateTime(timezone=True), nullable=False)
    type= database.Column(database.Boolean,nullable=False, default=False)
    # type==fasle means parties

    votes=database.relationship("Votes",back_populates="election")
    #presents all votes in this elections

    def __repr__(self):
        return {"id": self.id, "idElection": self.idElection}




class Participants(database.Model):
    __tablename__="participants"

    id=database.Column(database.Integer,primary_key=True)
    name=database.Column(database.String(256),nullable=False)
    type=database.Column(database.Boolean, nullable=False, default=False)
    # type==fasle means parties
    def __repr__(self):
        return {"id":self.id,"name":self.name}

class Votes(database.Model):
    __tablename__="votes"

    id = database.Column(database.Integer, primary_key=True)
    guid=database.Column(database.String(36),nullable=False)
    jmbg=database.Column(database.String(13),nullable=False)
    idElection=database.Column(database.Integer, database.ForeignKey("elections.id"),nullable=False)
    pollNumber = database.Column(database.Integer, nullable=False)
    isValid=database.Column(database.String(256), default=None)

    election=database.relationship("Elections", back_populates="votes")
