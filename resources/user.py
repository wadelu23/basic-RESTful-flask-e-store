from blacklist import BLACKLIST
from flask_restx import (
    Resource,
    reqparse,
    fields,
    Namespace
)
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt
)
from models.user import UserModel

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username',
                          type=str,
                          required=True,
                          help="This is field cannot blank")
_user_parser.add_argument('password',
                          type=str,
                          required=True,
                          help="This is field cannot blank")

api = Namespace("users", description="Users related operations")

_user_list = api.model('_user_list', {
    'id': fields.Integer(readonly=True, description="The user identifier"),
    'username': fields.String(required=True, description="The user name"),
})
_user_create = api.model('_user_create', {
    'username': fields.String(required=True, description="The username"),
    'password': fields.String(required=True, description="The user password"),
})


@api.route('/register')
@api.response(201, "User created successfully")
@api.response(400, "that username already exists.")
class UserRegister(Resource):
    @api.doc("regist user")
    @api.expect(_user_create)
    @api.marshal_with(_user_list)
    def post(self):
        """regist a user"""
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            api.abort(400,'that username already exists.')
            return

        user = UserModel(**data)
        user.save_to_db()

        return user, 201


@api.route('/')
class UserList(Resource):
    @api.doc("list_users")
    @api.marshal_list_with(_user_list, envelope='data')
    def get(cls):
        """list all user"""
        user = UserModel.find_all()
        if not user:
            api.abort(404)
            return
        return user, 200


@api.route('/<int:user_id>')
@api.param("user_id", "The user identifier")
@api.response(404, "User not found")
class User(Resource):
    @api.marshal_list_with(_user_list)
    def get(self, user_id):
        """get a user"""
        user = UserModel.find_by_id(user_id)
        if not user:
            api.abort(404,"User not found")
            return
        return user, 200

    @api.response(200, "User deleted.")
    def delete(self, user_id):
        """Delete user"""
        user = UserModel.find_by_id(user_id)
        if not user:
            api.abort(404,'User not found')
            return
        user.delete_from_db()
        return {'message': 'User deleted.'}, 200

@api.route('/login')
@api.response(401, "Invalid Credentials!")
@api.response(200, "Success")
class UserLogin(Resource):
    @api.expect(_user_create)
    def post(self):
        """user login"""
        data = _user_parser.parse_args()

        user = UserModel.find_by_username(data['username'])

        if user and safe_str_cmp(user.password, data['password']):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200

        return {"message": "Invalid Credentials!"}, 401

@api.route('/logout')
class UserLogout(Resource):
    @api.doc(security='apikey')
    @jwt_required()
    def post(self):
        """logout"""
        jti = get_jwt()["jti"]
        BLACKLIST.add(jti)
        return {
            'message': 'Successfuly Logged out.'
        }, 200

@api.route('/refresh')
class TokenRefresh(Resource):
    @api.doc(security='apikey')
    @jwt_required(refresh=True)
    def post(self):
        """refresh access_token"""
        current_user = get_jwt()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}
