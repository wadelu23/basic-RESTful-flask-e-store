from flask_restx import (
    Resource,
    reqparse,
    fields,
    Namespace
)
from flask_restx.marshalling import marshal
from models.store import StoreModel
from models.item import ItemModel


api = Namespace("stores",
                description="Stores related operations")

_item_list = api.model('_item_list', {
    'id': fields.Integer(
        readonly=True,
        description="The user identifier"
    ),
    'name': fields.String(
        required=True,
        description="The item name"
    ),
    'price': fields.Integer(
        required=True,
        description="The item price"
    ),
})

_store_list = api.model('_store_list', {
    'id': fields.Integer(
        readonly=True,
        description="The user identifier"
    ),
    'name': fields.String(
        required=True,
        description="The store name"
    ),
    'items': fields.List(
        fields.Nested(_item_list),
        description="The store's item"
    ),
})


@api.route('/<name>')
class Store(Resource):
    @api.response(404, 'Store not found.')
    @api.marshal_with(_store_list)
    def get(self, name):
        """get a store"""
        store = StoreModel.find_by_name(name)
        if store:
            return store
        api.abort(404)
        return

    @api.response(201, 'Success')
    @api.response(400, 'store name already exists')
    def post(self, name):
        """create a store"""
        if StoreModel.find_by_name(name):
            api.abort(404, "A store with name '{}' already exists.".format(name))
            return

        store = StoreModel(name)
        try:
            store.save_to_db()
        except:
            return {"message": "An error occurred while creating the store."}, 500

        return marshal(store, _store_list), 201

    def delete(self, name):
        """delete store"""
        store = StoreModel.find_by_name(name)

        if store:
            store.delete_from_db()

        return {'message': 'Store deleted'}


@api.route('/')
class StoreList(Resource):
    @api.marshal_with(_store_list)
    def get(self):
        """list all stores"""
        return StoreModel.find_all()
