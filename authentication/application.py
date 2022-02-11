from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, User, Role
from email.utils import parseaddr
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_
from re import search
from roleCheckDecorator import roleCheck

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)



def passwordCorrect(password):
    if len(password) < 8 or len(password) > 256:
        return False
    if not search("[0-9]", password):
        return False
    if not search("[a-z]", password):
        return False
    if not search("[A-Z]", password):
        return False
    return True


def jmbgCorrect(jmbg):
    # a b c d e f g h i j k l m
    # m = 11 − (( 7×(a + g) + 6×(b + h) + 5×(c + i) + 4×(d + j) + 3×(e + k) + 2×(f + l) ) mod 11)
    # 0101994700000
    if len(jmbg) < 13:
        return False;

    try:
        dan = int(jmbg[0:2:1])
        mesec = int(jmbg[2:4:1])
        godina = int(jmbg[4:7:1])
        region = int(jmbg[7:9:1])
        osoba = int(jmbg[9:12:1])
        kBr = int(jmbg[12])
        k = 11 - ((7 * (int(jmbg[0]) + int(jmbg[6])) + 6 * (int(jmbg[1]) + int(jmbg[7]))
                   + 5 * (int(jmbg[2]) + int(jmbg[8])) + 4 * (int(jmbg[3]) + int(jmbg[9]))
                   + 3 * (int(jmbg[4]) + int(jmbg[10])) + (2 * (int(jmbg[5]) + int(jmbg[11])))) % 11)

        if (k == 10 or k == 11) and kBr != 0:
            return False
        elif (k >= 1 and k <= 9) and k != kBr:
            return False
        if dan > 31 or dan < 1 or mesec > 12 or mesec < 1 or godina < 0 or godina > 999 \
                or region < 70 or region > 99 or osoba < 0 or osoba > 999:
            return False
    except:
        return False
    return True

@application.route("/delete",methods=["POST"])
@roleCheck(role=1)
def deleteUser():
    email = request.json.get("email", "")

    emailEmpty = len(email) == 0
    if (emailEmpty):
        return jsonify({"message": "Field email is missing."}), 400
    result = parseaddr(email)
    if not ("@" in parseaddr(email)[1]) or not(".com" in parseaddr(email)[1]):
        return jsonify({"message": "Invalid email."}), 400
    user=User.query.filter(User.email==email).first()
    if (not user):
        return jsonify({"message": "Unknown user."}), 400
    database.session.delete(user)
    database.session.commit()
    return Response(status=200)



@application.route("/refresh",methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity=get_jwt_identity();
    refreshClaims=get_jwt()

    additionalClaims={
        "jmbg": refreshClaims["jmbg"],
        "forename":refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "roles": refreshClaims["roles"],
        "ime":refreshClaims["ime"]
    }
    accesToken=create_access_token(identity=identity,additional_claims=additionalClaims)
    return jsonify({"accessToken":accesToken}),200


@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0
    if (emailEmpty):
        return jsonify({"message": "Field email is missing."}), 400
    if passwordEmpty:
        return jsonify({'message': 'Field password is missing.'}), 400

    result = parseaddr(email)
    if not ("@" in parseaddr(email)[1])or not(".com" in parseaddr(email)[1]):
        return jsonify({"message": "Invalid email."}), 400
    user = User.query.filter(and_(User.email == email, User.password == password)).first()

    if (not user):
        return jsonify({"message": "Invalid credentials."}), 400

    additionalClains = {
        "jmbg":user.id,
        "forename": user.forename,
        "surname": user.surname,
        "roles": user.roleId,
        "ime":Role.query.filter(Role.id==user.roleId).first().name
    }

    accestoken = create_access_token(identity=user.email, additional_claims=additionalClains)
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClains)

    return jsonify({"accessToken": accestoken, "refreshToken": refreshToken}), 200


@application.route("/register", methods=["POST"])
def register():
    jmbg = request.json.get("jmbg", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    isJmbgEmpty = len(jmbg) == 0
    isForenameEmpty = len(forename) == 0
    isSurnameEmpty = len(surname) == 0
    isEmailEmpty = len(email) == 0
    isPasswordEmpty = len(password) == 0

    if isJmbgEmpty:
        return jsonify({'message': 'Field jmbg is missing.'}), 400;
    if isForenameEmpty:
        return jsonify({"message": "Field forename is missing."}), 400
    if isSurnameEmpty:
        return jsonify({"message": "Field surname is missing."}), 400
    if isEmailEmpty:
        return jsonify({"message": "Field email is missing."}), 400
    if isPasswordEmpty:
        return jsonify({"message": "Field password is missing."}), 400

    if not jmbgCorrect(jmbg):
        return jsonify({"message": "Invalid jmbg."}),400
    mailResult = parseaddr(email);
    # prosledjujemo string koji proveramo a dobijamo torku sa dva elementa od koga je u drugom email ako u je dobrom formatu
    if not ("@" in mailResult[1])or not(".com" in mailResult[1]):
        return jsonify({"message": "Invalid email."}), 400
    if not passwordCorrect(password):
        return jsonify({"message": "Invalid password."}), 400

    users = User.query.filter(User.email == email).count();
    if users > 0:
        return jsonify({"message": "Email already exists."}), 400

    role = Role.query.filter(Role.name == "user").first();

    users = User.query.filter(User.id == jmbg).count();
    if (users > 0):
        return jsonify({"message": "JMBG already exists."}), 400

    user = User(id=jmbg, email=email, password=password, forename=forename, surname=surname, roleId=role.id)
    database.session.add(user)
    database.session.commit()

    return Response(status=200)


@application.route("/", methods=["GET"])
def hello():
    return str("mirko  slavko")


if (__name__ == "__main__"):
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
