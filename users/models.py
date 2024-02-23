from flask import Flask,jsonify
import uuid
from passlib.hash import pbkdf2_sha256


class User:
    def signup(self,name,email,password):
        user={
            "_id": uuid.uuid4().hex,
            "Name":name,
            "Email":email,
            "password":password

        }
        user['password']=pbkdf2_sha256.hash(user['password'])

      
        return user