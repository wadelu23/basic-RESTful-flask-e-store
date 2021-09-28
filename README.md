# Basic-Flask-RESTApi-e-book
> 簡易 REST API 架構
> 使用者建立與JWT驗證，管理商店與其物品
> 
> 此處記錄一些工具使用方式以及Heroku相關建置
> 
> 詳細 REST API 觀念
> 可參考[API 是什麼? RESTful API 又是什麼?](https://medium.com/itsems-frontend/api-%E6%98%AF%E4%BB%80%E9%BA%BC-restful-api-%E5%8F%88%E6%98%AF%E4%BB%80%E9%BA%BC-a001a85ab638)

[Heroku上的此專案展示](https://flask-restful-api-stores.herokuapp.com/)

`main` 分支可供 heroku 部署測試用
( heroku 需設定 FLASK_ENV )


可使用 [Postman](https://www.postman.com/) 或Swagger UI[官網例子](https://petstore.swagger.io/?_ga=2.98194327.923384134.1632810347-1794820871.1632719683) 測試API

![image](https://github.com/wadelu23/MarkdownPicture/blob/main/swaggerUI/swaggerUI001.png?raw=true)

![image](https://github.com/wadelu23/MarkdownPicture/blob/main/swaggerUI/swaggerUI002.png?raw=true)


---

目錄
- [Basic-Flask-RESTApi-e-book](#basic-flask-restapi-e-book)
  - [使用工具](#使用工具)
  - [簡述-API](#簡述-api)
  - [REST API 資源概念](#rest-api-資源概念)
  - [優劣勢](#優劣勢)
  - [筆記](#筆記)
    - [flask-restx](#flask-restx)
      - [Namespace](#namespace)
      - [Basic Usage](#basic-usage)
      - [@api.param](#apiparam)
      - [@api.response()](#apiresponse)
      - [@api.expect()](#apiexpect)
      - [api.abort](#apiabort)
    - [flask_jwt_extended](#flask_jwt_extended)
      - [Basic Usage](#basic-usage-1)
      - [additional_claims_loader](#additional_claims_loader)
      - [JWT Revoking Blocklist](#jwt-revoking-blocklist)
    - [Flask-SQLAlchemy](#flask-sqlalchemy)
      - [Simple Example](#simple-example)
      - [Select, Insert, Delete](#select-insert-delete)
      - [backref and back_populates](#backref-and-back_populates)
    - [部署](#部署)
      - [specify a Python runtime](#specify-a-python-runtime)
      - [Procfile](#procfile)
      - [uwsgi.ini](#uwsgiini)


## 使用工具
* [Flask](https://flask.palletsprojects.com/en/2.0.x/)
* [Flask-RESTX](https://flask-restx.readthedocs.io/en/latest/)(可自動產生 Swagger UI)
* [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/en/stable/)
* [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)


## 簡述-API
API，全名 Application Programming Interface
服務供應者提供的接口，給需要的人依照API的格式規範，傳送特定資料等，來利用該服務。

舉例來說，店面的官網會利用Google Map來讓使用者可直接看到地圖，便能比文字地址更快了解大概位置，這就是利用Google Map API去取得這項服務。(服務的收費標準不一，要看服務商規範)

## REST API 資源概念

網址(表示某一資源)與 [HTTP 請求方法](https://developer.mozilla.org/zh-TW/docs/Web/HTTP/Methods)搭配來操作資源，而資源呈現方式常用 [JSON](https://zh.wikipedia.org/wiki/JSON)

舉例:(操作`product`資源相關動作)

非REST風格(自訂)
| 目的     | HTTP Method | 網址            |
| -------- | ----------- | --------------- |
| 新增     | POST        | /addProduct     |
| 取得全部 | GET         | /getAllProducts |
| 更新     | POST        | /updateProduct  |

網址組成自訂，所以必須詳讀API規範來使用，較難推估同一資源的網址。

而如果是REST風格則變成
| 目的     | HTTP Method | 網址      |
| -------- | ----------- | --------- |
| 新增     | POST        | /product  |
| 更新     | PUT         | /product  |
| 取得全部 | GET         | /products |

留意網址中的 product
* product 代表一個資源 => 一個產品
* products 代表一組資源 => 多個產品

也可單用products來代表此種資源，不分一個或一組

## 優劣勢

有直觀簡短的統一網址來表示資源，搭配HTTP Method理解，也使資源相互的依賴性降低，能彈性組合來對應情形，但同時也可能是缺點。

例如:`取得某產品的完整製造工廠資訊`

並非每次都需要看到完整的製造工廠資訊，所以通常不會一開始就把完整工廠資訊放進產品的製造工廠資訊內，而是放一些簡單資訊，例如廠代號ID與廠名，如有需要再拿ID去找出完整工廠資訊。

因此`取得某產品的完整製造工廠資訊`，就需要兩次訪問API
1. 第一次拿到某產品資訊
2. 第二次則拿著其中的工廠ID訪問API，取得完整工廠資訊

## 筆記
resource中盡量不要有query語句，將那些語句放在model中，讓resource呼叫method，看起來更簡潔
```python
UserModel.query.filter_by(id=_id).first()

UserModel.find_by_id(user_id)
```
### flask-restx
#### Namespace
```python
# Namespace is to API what flask.Blueprint is for flask.Flask.
# Group resources together.
api = Namespace("cats", description="Cats related operations")
```
#### Basic Usage
```python
from flask_restx import Resource, fields

# You can define a dict or OrderedDict of fields whose keys are names of attributes or keys on the object to render,
# and whose values are a class that will format & return the value for that field. 
model = api.model('Model', {
    'name': fields.String,
    'address': fields.String,
    'date_updated': fields.DateTime(dt_format='rfc822'),
})

@api.route('/todo')
class Todo(Resource):
  # The decorator marshal_with() is what actually takes your data object and applies the field filtering.
  # The marshalling can work on single objects, dicts, or lists of objects.
    @api.marshal_with(model, envelope='resource')
    def get(self, **kwargs):
        return db_get_todo()
# envelope – optional key that will be used to envelop the serialized response

# functionally equivalent to
class Todo(Resource):
    def get(self, **kwargs):
        return marshal(db_get_todo(), model), 200
```
```python
@api.route("/")
class CatList(Resource):
    @api.doc("list_cats")
    @api.marshal_list_with(cat) # A shortcut decorator for marshal_with() with as_list=True
    def get(self):
        """List all cats"""
        return CATS
```
#### @api.param
```python
# Parameters from the URL path are documented automatically.
# You can provide additional information using the params keyword argument of the api.doc() decorator:

@api.route('/my-resource/<id>')
@api.doc(params={'id': 'An ID'})
class MyResource(Resource):
    pass

# or by using the api.param shortcut decorator:
@api.route('/my-resource/<id>')
@api.param('id', 'An ID')
class MyResource(Resource):
    pass
```
#### @api.response()
```python
# The @api.response() decorator allows you to document the known responses
# and is a shortcut for @api.doc(responses='...').
@api.route('/my-resource/')
class MyResource(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Validation Error')
    def get(self):
        pass


@api.route('/my-resource/')
class MyResource(Resource):
    @api.doc(responses={
        200: 'Success',
        400: 'Validation Error'
    })
    def get(self):
        pass
```
#### @api.expect()
The @api.expect() decorator allows you to specify the expected input fields.
```python
resource_fields = api.model('Resource', {
    'name': fields.String,
})

@api.route('/my-resource/<id>')
class MyResource(Resource):
    @api.expect(resource_fields)
    def get(self):
        pass
```
#### api.abort
Properly abort the current request.

Raise a HTTPException for the given status code.

Attach any keyword arguments to the exception for later processing.

```python
if todo_id not in TODOS:
  api.abort(404, "Todo {} doesn't exist".format(todo_id))
```
### flask_jwt_extended
#### Basic Usage
```python
from flask import Flask
from flask import jsonify
from flask import request

from flask_jwt_extended import (
  create_access_token,
  get_jwt_identity,
  jwt_required,
  JWTManager
)

app = Flask(__name__)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)


# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if username != "test" or password != "test":
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)


# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


if __name__ == "__main__":
    app.run()
```
#### additional_claims_loader
```python
# Using the additional_claims_loader, we can specify a method that will be
# called when creating JWTs. The decorated method must take the identity
# we are creating a token for and return a dictionary of additional
# claims to add to the JWT.
@jwt.additional_claims_loader
def add_claims_to_access_token(identity):
     return = {
         "aud": "some_audience",
         "foo": "bar",
         "upcase_name": identity.upper(),
     }
```
#### JWT Revoking Blocklist
[完整說明](https://flask-jwt-extended.readthedocs.io/en/stable/blocklist_and_token_revoking/?highlight=get_jwt%20jti#jwt-revoking-blocklist)

JWT revoking is a mechanism for preventing an otherwise valid JWT from accessing your routes while still letting other valid JWTs in.

To utilize JWT revoking in this extension, you must defining a callback function via the token_in_blocklist_loader() decorator.
```python
# Setup our redis connection for storing the blocklisted tokens. You will probably
# want your redis instance configured to persist data to disk, so that a restart
# does not cause your application to forget that a JWT was revoked.
jwt_redis_blocklist = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)

# Callback function to check if a JWT exists in the redis blocklist
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None

@app.route("/login", methods=["POST"])
def login():
    access_token = create_access_token(identity="example_user")
    return jsonify(access_token=access_token)

# Endpoint for revoking the current users access token. Save the JWTs unique
# identifier (jti) in redis. Also set a Time to Live (TTL)  when storing the JWT
# so that it will automatically be cleared out of redis after the token expires.
@app.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    jwt_redis_blocklist.set(jti, "", ex=ACCESS_EXPIRES)
    return jsonify(msg="Access token revoked")
```
### Flask-SQLAlchemy

[官方文件](https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/#declaring-models)

#### Simple Example
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username
```
#### Select, Insert, Delete
[官方文件](https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/#select-insert-delete)
```python
# Insert
from yourapp import User
me = User('admin', 'admin@example.com')
db.session.add(me)
db.session.commit()

# Delete
db.session.delete(me)
db.session.commit()

# Querying Records
User.query.filter_by(username='peter').first()

User.query.filter(User.email.endswith('@example.com')).all()

User.query.order_by(User.username).all()

User.query.limit(1).all()

User.query.get(1) # by primary key
```
#### backref and back_populates
[SQLAlchemy官方詳細說明](https://docs.sqlalchemy.org/en/14/orm/backref.html#linking-relationships-with-backref)
```python
from sqlalchemy import Integer, ForeignKey, String, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    addresses = relationship("Address", backref="user")

class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))
```
The above configuration establishes a collection of Address objects on User called User.addresses. It also establishes a .user attribute on Address which will refer to the parent User object.

In fact, the relationship.backref keyword is only a common shortcut for placing a second relationship() onto the Address mapping, including the establishment of an event listener on both sides which will mirror attribute operations in both directions.
(使用backref，則不用在第二張表上宣告relationship)

The above configuration is equivalent to:
```python
from sqlalchemy import Integer, ForeignKey, String, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    addresses = relationship("Address", back_populates="user")

class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))

    user = relationship("User", back_populates="addresses")
```
(back_populates 則需在兩張表中使用，雖然顯得繁瑣，但是也更清晰看到這張表有哪些屬性)

### 部署
#### specify a Python runtime
To specify a Python runtime, add a runtime.txt file to your app’s root directory that declares the exact version number to use:
```bash
cat runtime.txt
python-3.9.7
```

#### Procfile
```Procfile
web: uwsgi uwsgi.ini
```
啟用名為 web 的應用
用 uwsgi 執行 uwsgi.ini 中的設定

#### uwsgi.ini
```ini
[uwsgi]
# 協議方式，:$(PORT)是配合heroku
http-socket = :$(PORT)
# 開啟一個主進程
master = true
die-on-term = true
module = run:app
memory-report = true
```
[What is –die-on-term?](https://uwsgi-docs.readthedocs.io/en/latest/Upstart.html#what-is-die-on-term)




參考引用

[API 是什麼? RESTful API 又是什麼?](https://medium.com/itsems-frontend/api-%E6%98%AF%E4%BB%80%E9%BA%BC-restful-api-%E5%8F%88%E6%98%AF%E4%BB%80%E9%BA%BC-a001a85ab638)

[HTTP 請求方法](https://developer.mozilla.org/zh-TW/docs/Web/HTTP/Methods)

[JSON簡介](https://zh.wikipedia.org/wiki/JSON)

[flask config 不同環境設定檔設置方式](https://flask.palletsprojects.com/en/2.0.x/config/#development-production)

[REST APIs with Flask and Python](https://www.udemy.com/course/rest-api-flask-and-python/)
