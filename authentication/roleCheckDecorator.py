from flask_jwt_extended import  verify_jwt_in_request,get_jwt
from functools import  wraps
from flask import jsonify

def roleCheck(role):
    def innerRole(function):
        @wraps(function)
        def decorator(*arguments,**ketwordArguments):
            verify_jwt_in_request();
            claims=get_jwt()
            if(("roles"in claims))and (role == claims["roles"]):
                return function(*arguments,**ketwordArguments)
            else:
                return jsonify({"msg": "Missing Authorization Header"}),401
        return decorator
    return innerRole;