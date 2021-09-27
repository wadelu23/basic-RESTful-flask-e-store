from flask_restx import Api

from .user import api as user_api
# from .dog import api as dog_api

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

api = Api(
    title="E-Book API",
    version="1.0",
    authorizations=authorizations,
    description="A simple demo API",
)

api.add_namespace(user_api)
# api.add_namespace(dog_api)