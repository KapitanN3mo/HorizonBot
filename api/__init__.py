import importlib
import os
from datetime import *
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask import Flask
from flask import jsonify, request
from werkzeug.security import check_password_hash
import core
import json
import database
from api import scripts

with open("settings.json", 'r') as sf:
    settings = json.load(sf)
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = settings['jwt']['secret_key']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=5)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(seconds=5)
jwt = JWTManager(app)


@app.route('/login', methods=['GET'])
def login():
    bot = core.Bot.get_bot()
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    db_user = database.ApiUser().get_or_none(database.ApiUser.user_name == username)
    print(db_user)
    if db_user is None:
        return jsonify({'msg': 'Wrong password or username'}), 401
    if check_password_hash(db_user.password_hash, password):
        access_token = create_access_token(identity=db_user.user_id, fresh=True)
        refresh_token = create_refresh_token(identity=db_user.user_id)
        db_user.refresh_token = refresh_token
        db_user.save()
        ds_user = bot.get_user(db_user.user_id)
        data = {
            'name': ds_user.name,
            'avatar_url': ds_user.display_avatar.url
        }
        return jsonify(msg='ok', access_token=access_token, refresh_token=refresh_token, data=data), 200
    else:
        return jsonify({'msg': 'Wrong password or username'}), 401


@app.route('/text_message', methods=['GET'])
@jwt_required()
def get_text_message():
    bot = core.Bot.get_bot()
    guilds = scripts.get_user_admin_guilds(get_jwt_identity())
    guilds_id = [g.id for g in guilds]
    messages = database.TextBotMessage.select().where(database.TextBotMessage.guild_id.in_(guilds_id))
    complete_messages = []
    for mes in messages:
        guild = bot.get_guild(mes.guild_id)
        channel = guild.get_channel(mes.channel_id)
        message = bot.loop.create_task(channel.fetch_message(mes.message_id)).result()
        print(message.to_message_reference_dict())
        print(message.to_reference())
