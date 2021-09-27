from flask_restx import Api

from .user import api as user_api
from .item import api as item_api
from .store import api as store_api

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
    description="A simple demo API.<br> For manage users,stores,items.<br>Some route required JWT authorization",
)

api.add_namespace(user_api)
api.add_namespace(item_api)
api.add_namespace(store_api)
