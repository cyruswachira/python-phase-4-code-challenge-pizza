#!/usr/bin/env python3
import os
from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Restaurant, RestaurantPizza, Pizza

# Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Initialize Flask application
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Initialize database and migration
db.init_app(app)
migrate = Migrate(app, db)

# Initialize API
api = Api(app)

# Resource for handling multiple restaurants
class RestaurantsResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        result = [restaurant.to_dict() for restaurant in restaurants]
        for restaurant in result:
            restaurant.pop('restaurant_pizzas', None)
        return make_response(jsonify(result), 200)

api.add_resource(RestaurantsResource, "/restaurants")

# Resource for handling a single restaurant by ID
class RestaurantByIDResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        return make_response(jsonify(restaurant.to_dict()), 200)
    
    def delete(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return {"error": "Restaurant not found"}, 404

        db.session.delete(restaurant)
        db.session.commit()
        return {}, 204

api.add_resource(RestaurantByIDResource, "/restaurants/<int:id>")

# Resource for handling multiple pizzas
class PizzasResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        result = [pizza.to_dict() for pizza in pizzas]
        return make_response(jsonify(result), 200)

api.add_resource(PizzasResource, "/pizzas")

# Resource for handling restaurant pizzas
class RestaurantPizzasResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            price = int(data.get('price'))
            restaurant_pizza = RestaurantPizza(
                pizza_id=data.get('pizza_id'),
                restaurant_id=data.get('restaurant_id'),
                price=price
            )
            db.session.add(restaurant_pizza)
            db.session.commit()
            return make_response(jsonify(restaurant_pizza.to_dict()), 201)
        except ValueError:
            return {"errors": ["Price must be between 1 and 30"]}, 400
        except Exception:
            return {"errors": ["Validation errors"]}, 400

api.add_resource(RestaurantPizzasResource, "/restaurant_pizzas")

# Main entry point
if __name__ == "__main__":
    app.run(port=5555, debug=True)
