from flask_login import UserMixin
from app import mongo, login_manager
from bson.objectid import ObjectId
from datetime import datetime

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.email = user_data.get('email', '')
        self.email_confirmed = user_data.get('email_confirmed', False)

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

class Client:
    def __init__(self, client_data):
        self.id = str(client_data['_id'])
        self.name = client_data['name']
        self.email = client_data['email']
        self.phone = client_data['phone']
        self.address = client_data.get('address', '')
        self.notes = client_data.get('notes', '')

class Car:
    def __init__(self, car_data):
        self.id = str(car_data['_id'])
        self.make = car_data['make']
        self.model = car_data['model']
        self.year = car_data['year']
        self.price = car_data['price']
        self.sold = car_data.get('sold', False)
        self.client_id = car_data.get('client_id', None)

class Expense:
    def __init__(self, expense_data):
        self.id = str(expense_data['_id'])
        self.date = expense_data['date']
        self.amount = expense_data['amount']
        self.category = expense_data['category']
        self.description = expense_data['description']
        self.car_id = expense_data.get('car_id', None)