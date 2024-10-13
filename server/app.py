#!/usr/bin/env python3

from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# Initialize Flask-RESTful
api = Api(app)

# Index Route
@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

# RESTful API Routes
class RestaurantList(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants], 200

class RestaurantDetail(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return restaurant.to_dict(), 200
        else:
            return {"error": "Restaurant not found"}, 404

    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return '', 204
        else:
            return {"error": "Restaurant not found"}, 404

class PizzaList(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas], 200

class RestaurantPizzaCreate(Resource):
    def post(self):
        data = request.get_json()
        try:
            price = data['price']
            restaurant_id = data['restaurant_id']
            pizza_id = data['pizza_id']

            # Validate if restaurant and pizza exist
            restaurant = Restaurant.query.get(restaurant_id)
            pizza = Pizza.query.get(pizza_id)

            if not restaurant or not pizza:
                return {"errors": ["Invalid restaurant or pizza"]}, 400

            # Create new RestaurantPizza
            restaurant_pizza = RestaurantPizza(price=price, restaurant_id=restaurant_id, pizza_id=pizza_id)
            db.session.add(restaurant_pizza)
            db.session.commit()

            return restaurant_pizza.to_dict(), 201

        except Exception as e:
            return {"errors": [str(e)]}, 400

# Add routes to the API
api.add_resource(RestaurantList, '/restaurants')
api.add_resource(RestaurantDetail, '/restaurants/<int:id>')
api.add_resource(PizzaList, '/pizzas')
api.add_resource(RestaurantPizzaCreate, '/restaurant_pizzas')

# Run the app
if __name__ == '__main__':
    with app.app_context():
       db.create_all()  # Ensure tables are created before running
    app.run(port=5555, debug=True)
