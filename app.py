from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import (
    UserRegister,
    User,
    UserLogin,
    TokenRefresh
)
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from db import db


app = Flask(__name__)

app.config.from_object('config.DevelopmentConfig')

api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


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


api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')

if __name__ == '__main__':
    db.init_app(app)
    app.run()
