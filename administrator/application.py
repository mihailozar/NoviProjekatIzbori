

from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, Participants,Elections,Resaults,Votes
from email.utils import parseaddr
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_,or_,func
from re import search
from roleCheckDecorator import roleCheck
from datetime import datetime
import datetime as DATETIME
from dateutil import parser


application = Flask(__name__);
application.config.from_object(Configuration);

jwt=JWTManager(application)

@application.route("/createParticipant", methods=["POST"])
@roleCheck(role=1)
def createParticipant():
    name= request.json.get("name","")
    individual=request.json.get("individual",None)

    if(len(name)==0):
        return jsonify({'message':"Field name is missing."}),400
    if  individual==None:
        return jsonify({'message':"Field individual is missing."}),400

    participant=Participants(name=name,type=individual)
    database.session.add(participant)
    database.session.commit()

    return jsonify({'id':participant.id}),200


@application.route("/getParticipants", methods=["GET"])
@roleCheck(role=1)
def getParticipant():
    participants=[]
    for row in Participants.query.all():
        participants.append(
            {
                "id":row.id,
                "name":row.name,
                "individual":row.type
            }
        )
    return jsonify({"participants":participants}),200

@application.route("/createElection", methods=["POST"])
@roleCheck(role=1)
def createElection():
    start=request.json.get("start","")
    end= request.json.get("end","")
    individual=request.json.get("individual",None)
    participants=request.json.get("participants","")

    if start=="":
        return jsonify({"message":"Field start is missing."}),400
    if end=="":
        return jsonify({"message":"Field end is missing."}),400
    if  individual==None:
        return jsonify({"message":"Field individual is missing."}),400
    if participants=="":
        return jsonify({'message': 'Field participants is missing.'}),400

    try:
        normalStart = parser.parse(start)
        normalEnd = parser.parse(end)
        if normalStart >= normalEnd:
            return jsonify({"message": "Invalid date and time."}), 400
    except:
        return jsonify({"message": "Invalid date and time."}), 400

    if len(participants)<2 :
        return jsonify({'message': 'Invalid participants.'}), 400




    electionsArray=Elections.query.all()
    if(len(electionsArray)>0):
        for row in Elections.query.all():

            if (normalStart<row.start or normalStart==row.start ) and (normalEnd>row.end or normalEnd==row.end):
                return jsonify({"message": "Invalid date and time."}), 400
            elif (normalEnd > row.start or normalEnd==row.start) and (normalEnd<row.end or normalEnd==row.end):
                return jsonify({"message": "Invalid date and time."}), 400
            elif (normalStart>row.start  or normalStart== row.start) and (normalStart<row.end or normalStart==row.end):
                return jsonify({"message": "Invalid date and time."}), 400

    try:
        for row in participants:
            if Participants.query.filter(and_(Participants.id==row,Participants.type==individual)).count()!=1:
                return jsonify(message='Invalid participants.'), 400;
    except Exception :
        return jsonify({'message': 'Invalid participants.'}), 400

    election=Elections(start=normalStart,end=normalEnd,type=individual)
    database.session.add(election)
    database.session.commit()
    polNumbers=[]
    i=1;
    for row in participants:
        res=Resaults(idElection=election.id,idParticipants=row,participantNumber=i)
        i+=1
        database.session.add(res)
        database.session.commit()
        polNumbers.append(res.participantNumber)
    return jsonify({"pollNumbers":polNumbers}),200


@application.route("/getElections", methods=["GET"])
@roleCheck(role=1)
def getElections():
    array=[]
    electoins=Elections.query.all()
    for election in electoins:

        array.append({
                    "id":election.id,
                    "start":election.start.isoformat(),
                    "end":election.end.isoformat(),
                    "individual":election.type,
                    "participants":[
                        *[part.__repr__() for part in Participants.query.join(Resaults).filter(Resaults.idElection==election.id).all() ]
                    ]
                }
        )
    return jsonify({"elections":array}),200

@application.route("/getResults", methods=["GET"])
@roleCheck(role=1)
def getResaults():
    idElection=request.args.get("id",None)

    if idElection==None:
        return jsonify({"message":"Field id is missing."}),400
    try:
        idElection=int(idElection)
    except:
        return jsonify({"message":"Election does not exist."}),400

    electionFromDB=Elections.query.filter(Elections.id==idElection).first()

    if electionFromDB==None:
        return jsonify({"message":"Election does not exist."}),400

    now = DATETIME.datetime.now().replace(microsecond=0).isoformat()

    if electionFromDB.start<=datetime.fromisoformat(now) and electionFromDB.end>=datetime.fromisoformat(now):
        return jsonify({"message": "Election is ongoing."}), 400
    if electionFromDB.type:
        resaults=getResaultsIndividual(electionFromDB)
    else:
        resaults=getResaultsNoIndividual(electionFromDB)
    return jsonify(resaults),200


def getResaultsIndividual(election):
    # parlament
    validVotes=[vote for vote in election.votes if vote.isValid==None]
    numberOfVotes = len(validVotes)
    invalidVotes=[vote for vote in election.votes if vote.isValid!=None]
    participants = []
    for result in Resaults.query.filter(Resaults.idElection==election.id).all():
        participants.append({
            "pollNumber":result.participantNumber,
            "name":Participants.query.filter(Participants.id==result.idParticipants).first().name,
            "result":round(len([vote for vote in validVotes if vote.pollNumber==result.participantNumber])/ numberOfVotes, 2)
        })
    arrayInvalidVotes=[]
    for vote in invalidVotes:
       arrayInvalidVotes.append({
           "electionOfficialJmbg":vote.jmbg,
           "ballotGuid":vote.guid,
           "pollNumber":vote.pollNumber,
           "reason":vote.isValid
       })

    return {"participants":participants,"invalidVotes":arrayInvalidVotes}


def getResaultsNoIndividual(election):
    participantsInElection=[{"idPart":res.idParticipants,
                             "numberOfVotes":0,
                             "devidedNumber":0,
                             "numberOfMandatas":0,
                             "pollNumber":res.participantNumber
                             }for res in Resaults.query.filter(Resaults.idElection==election.id).all()]
    for participant in participantsInElection:
        a=len([vote for vote in election.votes if vote.isValid==None and vote.pollNumber==participant["pollNumber"]])
        allVotes=len([vote for vote in election.votes if vote.isValid==None])
        participant["numberOfVotes"]=a if a>=float(allVotes*0.05) else 0
        participant["devidedNumber"]=participant["numberOfVotes"]



    numberOfMandates=250


    while numberOfMandates > 0:
        participantsInElection.sort(reverse=True, key=mySort)
        tmpArray=[]
        i=1
        tmpArray.append(participantsInElection[0])
        while  participantsInElection[0]["devidedNumber"]==participantsInElection[i]["devidedNumber"]:
            tmpArray.append(participantsInElection[i])
            i += 1
            if i>=len(participantsInElection):
                break

        if len(tmpArray)>1:
            tmpArray.sort(reverse=True, key=mySort2)
        partCompute=tmpArray[0]
        partCompute["devidedNumber"]=float(partCompute["numberOfVotes"]/(partCompute["numberOfMandatas"]+1))
        partCompute["numberOfMandatas"]+=1
        tmpArray.clear()
        numberOfMandates-=1


    mandati=[{"pollNumber":part["pollNumber"],
             "name":Participants.query.filter(Participants.id==part["idPart"]).first().name,
             "result":part["numberOfMandatas"]
             } for part in participantsInElection]



    invalidVotes = [vote for vote in election.votes if vote.isValid != None]

    arrayInvalidVotes = []
    for vote in invalidVotes:
        arrayInvalidVotes.append({
            "electionOfficialJmbg": vote.jmbg,
            "ballotGuid": vote.guid,
            "pollNumber": vote.pollNumber,
            "reason": vote.isValid
        })
    return {"participants": mandati, "invalidVotes": arrayInvalidVotes}



def mySort(part):
    return part["devidedNumber"]
def mySort2(part):
    return part["numberOfVotes"]

@application.route("/modifikacija", methods=["GET"])
def modifikacija():
    ime=request.args.get("ime",None)
    id=request.args.get("id",None)

    if ime and id:
        # participant=Resaults.query.filter(Resaults.idElection==id).join(Participants).\
        #     filter(Participants.name.like(f"%{ime}%")).with_entities(Participants.id, Participants.name).all()
        participant=Resaults.query.filter(Resaults.idElection==id).join(Elections).join(Votes). \
            filter(and_( Votes.isValid==None, Votes.idElection==id)).group_by(Votes.pollNumber).\
            with_entities(Votes.idElection,Votes.pollNumber,func.count()).all()
    elif ime:
        participant=Participants.query.filter(Participants.name.like(f"%{ime}%")).\
            with_entities(Participants.id,Participants.name).all()
    else :
        participant=Resaults.query.filter(Resaults.idElection==id).join(Participants).\
            with_entities(Participants.id,Participants.name).all()


    return jsonify({"message":str(participant)}),200


if (__name__ == "__main__"):
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5003)
