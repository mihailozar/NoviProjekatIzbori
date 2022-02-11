import io

from flask import Flask, request, Response, jsonify
from configuration import Configuration

from email.utils import parseaddr
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_,or_
from re import search
from roleCheckDecorator import roleCheck
from datetime import datetime
import csv
import datetime

from redis import Redis



application = Flask(__name__);
application.config.from_object(Configuration);

jwt=JWTManager(application)


@application.route("/vote",methods=["POST"])
@roleCheck(role=2)
def vote():
    try:
        file = request.files.get("file", None);
    except:
        return jsonify({'message': 'Field file is missing.'}), 400
    if file==None:
        return jsonify({'message': 'Field file is missing.'}),400

    content = file.stream.read().decode("utf-8");
    stream = io.StringIO(content);
    reader = csv.reader(stream);
    line=0
    array=[]



    for row in reader:

        if len(row)!=2:
            return jsonify({"message":"Incorrect number of values on line "+str(line)+"."}),400
        try:
            if int(row[1])<1:
                return jsonify({"message":"Incorrect poll number on line "+str(line)+"."}),400
        except:
            return jsonify({"message": "Incorrect poll number on line " + str(line)+"."}), 400
        line+=1
        array.append(row)


    token=get_jwt()
    jmbg=token.get("jmbg","")


    for row in array:
        with Redis(host=Configuration.REDIS_HOST) as redis:
            redis.rpush(Configuration.REDIS_VOTES, row[0]+", "+row[1]+", "+jmbg+", "+datetime.datetime.now().replace(microsecond=0).isoformat())

    return Response(status=200)

@application.route("/getVote",methods=["GET"])
# @roleCheck(role=0)
def getVote():
    with Redis(host=Configuration.REDIS_HOST) as redis:
        poruka=redis.lpop(Configuration.REDIS_VOTES)
    return poruka


@application.route("/",methods=["GET"])
def index():
    return "Glasanje";


if (__name__ == "__main__"):

    application.run(debug=True, host="0.0.0.0", port=5001)