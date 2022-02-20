import json
from dt import timedelta
from flask import Flask
from flask import jsonify
from flask import request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

import database

app = Flask(__name__)

# with open("settings.json", 'r') as sf:
#     settings = json.load(sf)
app.config['JWT_SECRET_KEY'] = 'test'  # settings['jwt']['secret_key']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=10)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
jwt = JWTManager(app)


@app.route("/api/login", methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    db_user = database.ApiUser().get_or_none(database.ApiUser.user_name == username)
    print(db_user)
    if db_user is None:
        return jsonify({'msg': 'Bad username or password'}), 401
    if check_password_hash(db_user.password_hash, password):
        access_token = create_access_token(identity=username, fresh=True)
        refresh_token = create_refresh_token(identity=username)
        db_user.refresh_token = refresh_token
        db_user.save()
        return jsonify(msg='ok', access_token=access_token, refresh_token=refresh_token)
    else:
        return jsonify({'msg': 'Bad username or password'}), 401


@app.route('/refresh', methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity, fresh=False)
    return jsonify(access_token=access_token)


@app.route('/test', methods=["GET"])
@jwt_required(fresh=False)
def no_fresh():
    return jsonify(msg='no_fresh_ok')


@app.route('/test1', methods=["GET"])
@jwt_required(fresh=True)
def fresh():
    return jsonify(msg='fresh_ok')


if __name__ == '__main__':
    app.run()
