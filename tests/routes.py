import asyncio
import json
from datetime import timedelta
from flask import Flask
from flask import jsonify
from flask import request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

import core
from api.endpoints import message
import database

app = Flask(__name__)



@app.route('/refresh', methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity, fresh=False)
    return jsonify(access_token=access_token), 200


@app.route('/message', methods=['GET'])
@jwt_required(fresh=False)
def get_messages():
    user_id = get_jwt_identity()
    loop = core.Bot.get_bot().loop
    future = asyncio.run_coroutine_threadsafe(message.get_ordinary_messages(user_id), loop)
    result = future.result()
    if result[0]:
        result_code = 200
    else:
        result_code = 400
    return jsonify(result[1]), result_code


