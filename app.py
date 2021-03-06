import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from blacklist import BLACKLIST
from resources import api
from config import config

app = Flask(__name__)

flask_env = os.environ.get('FLASK_ENV') or 'default'

app.config.from_object(config[flask_env])

api.init_app(app)

jwt = JWTManager(app)


# Using the additional_claims_loader, we can specify a method that will be
# called when creating JWTs. The decorated method must take the identity
# we are creating a token for and return a dictionary of additional
# claims to add to the JWT.


@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    # identity就是user.id
    # create_access_token(identity=user.id, fresh=True)
    # 這裡先把判斷的值(1)寫在程式碼內
    # 實際上這值是從設定檔或是資料庫取得
    return {
        'is_admin': True if identity == 1 else False
    }


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    return jwt_payload['jti'] in BLACKLIST


@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'message': 'The token has expired',
        'error': 'token_expired'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'message': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'description': 'Request does not contain an access token.',
        'error': 'authorization_required'
    }), 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        'description': 'The token is not fresh.',
        'error': 'fresh_token_required'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'description': 'The token has been revoked.',
        'error': 'token_revoked'
    }), 401


if __name__ == '__main__':
    app.run()
