from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_serializer import SerializerMixin

# Define metadata with naming conventions
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

# Initialize SQLAlchemy with custom metadata
db = SQLAlchemy(metadata=metadata)
Base = declarative_base()

# Define Restaurant model
class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(String)
    pizzas = relationship('RestaurantPizza', back_populates='restaurant', cascade="all, delete-orphan")

    serialize_rules = ('-pizzas.restaurant',)

    def __repr__(self):
        return f"<Restaurant {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'restaurant_pizzas': [rp.to_dict(include_restaurant=False) for rp in self.pizzas]
        }

# Define Pizza model
class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    ingredients = Column(String)
    restaurants = relationship('RestaurantPizza', back_populates='pizza', cascade="all, delete-orphan")

    serialize_rules = ('-restaurants.pizza',)

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients
        }

# Define RestaurantPizza model
class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = Column(Integer, primary_key=True)
    price = Column(Integer, nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    pizza_id = Column(Integer, ForeignKey('pizzas.id'))

    restaurant = relationship('Restaurant', back_populates='pizzas')
    pizza = relationship('Pizza', back_populates='restaurants')

    serialize_rules = ('-restaurant.pizzas', '-pizza.restaurants')

    @validates('price')
    def validate_price(self, key, price):
        if not (1 <= price <= 30):
            raise ValueError("Price must be between 1 and 30")
        return price

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"

    def to_dict(self, include_restaurant=True):
        data = {
            'id': self.id,
            'price': self.price,
            'pizza_id': self.pizza_id,
            'restaurant_id': self.restaurant_id,
            'pizza': self.pizza.to_dict()
        }
        if include_restaurant:
            data['restaurant'] = {'id': self.restaurant.id, 'name': self.restaurant.name}
        return data
