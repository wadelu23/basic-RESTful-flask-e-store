from flask_restx import (
    Resource,
    reqparse,
    fields,
    Namespace
)
from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    get_jwt_identity
)
from flask_restx.marshalling import marshal
from models.item import ItemModel


api = Namespace("items", description="Items related operations")
_item_create = api.model('_item_create', {
    'price': fields.Float(required=True, description="The item price"),
    'store_id': fields.Integer(required=True, description="belong which store"),
})
_item_list = api.model('_item_list', {
    'id': fields.Integer(),
    'name': fields.String(),
    'price': fields.Float(),
    'store_id': fields.Integer(),
})
_item_name_list = api.model('_item_name_list', {
    'name': fields.String(),
})


@api.route('/<name>')
class Item(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help="This field cannot be left blank!")
    parser.add_argument('store_id',
                        type=int,
                        required=True,
                        help="every item needs a store id.")

    @api.doc(security='apikey')
    @jwt_required()
    @api.marshal_with(_item_list)
    @api.response(404, 'Item not found')
    def get(self, name):
        """get item by name"""
        item = ItemModel.find_by_name(name)
        if item:
            return item
        api.abort(404, 'Item not found')
        return

    @jwt_required(refresh=True)
    @api.doc(security='apikey')
    @api.expect(_item_create)
    def post(self, name):
        """create a item"""
        if ItemModel.find_by_name(name):
            return {'message': "An item with name '{}' already exists.".format(name)}, 400

        data = self.parser.parse_args()

        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {"message": "An error occurred inserting the item."}, 500

        return marshal(item, _item_list), 201

    @api.doc(security='apikey')
    @jwt_required()
    def delete(self, name):
        """delete item"""
        claims = get_jwt()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401

        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()

        return {'message': 'Item deleted'}

    @api.doc(security='apikey')
    @jwt_required()
    @api.marshal_with(_item_list)
    def put(self, name):
        """update item"""
        data = self.parser.parse_args()
        item = ItemModel.find_by_name(name)

        if item:
            item.price = data['price']
        else:
            item = ItemModel(name, **data)

        item.save_to_db()

        return item


@api.route('/')
class ItemList(Resource):
    @api.doc(security='apikey')
    @jwt_required(optional=True)
    def get(self):
        """list all item"""
        user_id = get_jwt_identity()
        all_items = ItemModel.find_all()

        if user_id:
            return {
                'items': marshal(all_items, _item_list)
            }, 200

        return {
            'items': marshal(all_items, _item_name_list),
            'message': 'More data available if you log in.'
        }, 200
