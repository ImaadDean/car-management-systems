from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import mongo
from app.cars import bp
from bson.objectid import ObjectId

@bp.route('/cars')
@login_required
def car_list():
    cars = mongo.db.cars.find()
    return render_template('cars/car_list.html', cars=cars)

@bp.route('/cars/sellable')
@login_required
def sellable_cars():
    cars = mongo.db.cars.find({'sold': False})
    return render_template('cars/sellable_cars.html', cars=cars)

@bp.route('/cars/add', methods=['GET', 'POST'])
@login_required
def add_car():
    if request.method == 'POST':
        car = {
            'make': request.form.get('make'),
            'model': request.form.get('model'),
            'year': request.form.get('year'),
            'price': request.form.get('price'),
            'sold': False
        }
        mongo.db.cars.insert_one(car)
        flash('Car added successfully', 'success')
        return redirect(url_for('cars.car_list'))
    return render_template('cars/add_car.html')

@bp.route('/cars/edit/<car_id>', methods=['GET', 'POST'])
@login_required
def edit_car(car_id):
    car = mongo.db.cars.find_one({'_id': ObjectId(car_id)})
    if request.method == 'POST':
        updated_car = {
            'make': request.form.get('make'),
            'model': request.form.get('model'),
            'year': request.form.get('year'),
            'price': request.form.get('price')
        }
        mongo.db.cars.update_one({'_id': ObjectId(car_id)}, {'$set': updated_car})
        flash('Car updated successfully', 'success')
        return redirect(url_for('cars.car_list'))
    return render_template('cars/edit_car.html', car=car)

@bp.route('/cars/delete/<car_id>')
@login_required
def delete_car(car_id):
    mongo.db.cars.delete_one({'_id': ObjectId(car_id)})
    flash('Car deleted successfully', 'success')
    return redirect(url_for('cars.car_list'))

@bp.route('/cars/sell/<car_id>', methods=['GET', 'POST'])
@login_required
def sell_car(car_id):
    car = mongo.db.cars.find_one({'_id': ObjectId(car_id)})
    clients = mongo.db.clients.find()
    
    if request.method == 'POST':
        client_type = request.form.get('client_type')
        purchase_amount = float(request.form.get('purchase_amount'))
        payment_amount = float(request.form.get('payment_amount'))
        remaining_balance = float(request.form.get('remaining_balance'))
        next_payment_date = request.form.get('next_payment_date')
        
        if client_type == 'existing':
            client_id = request.form.get('client_id')
            client = mongo.db.clients.find_one({'_id': ObjectId(client_id)})
        else:
            # Create a new client
            new_client = {
                'name': request.form.get('name'),
                'email': request.form.get('email'),
                'phone': request.form.get('phone'),
                'address': request.form.get('address'),
                'total_balance': remaining_balance
            }
            result = mongo.db.clients.insert_one(new_client)
            client_id = str(result.inserted_id)
            client = new_client

        # Update the car as sold and associate it with the client
        mongo.db.cars.update_one(
            {'_id': ObjectId(car_id)},
            {'$set': {
                'sold': True,
                'client_id': client_id,
                'purchase_amount': purchase_amount,
                'payment_amount': payment_amount,
                'remaining_balance': remaining_balance,
                'next_payment_date': datetime.strptime(next_payment_date, '%Y-%m-%d')
            }}
        )
        
        # Create a new sale record
        sale_record = {
            'car_id': car_id,
            'client_id': client_id,
            'purchase_amount': purchase_amount,
            'payment_amount': payment_amount,
            'remaining_balance': remaining_balance,
            'next_payment_date': datetime.strptime(next_payment_date, '%Y-%m-%d'),
            'sale_date': datetime.utcnow()
        }
        mongo.db.sales.insert_one(sale_record)
        
        # If there's a remaining balance, create or update a debt record
        if remaining_balance > 0:
            debt_record = {
                'client_id': client_id,
                'car_id': car_id,
                'total_amount': purchase_amount,
                'remaining_balance': remaining_balance,
                'next_payment_date': datetime.strptime(next_payment_date, '%Y-%m-%d'),
                'last_updated': datetime.utcnow()
            }
            mongo.db.debts.update_one(
                {'client_id': client_id, 'car_id': car_id},
                {'$set': debt_record},
                upsert=True
            )

            # Update client's total balance
            mongo.db.clients.update_one(
                {'_id': ObjectId(client_id)},
                {'$inc': {'total_balance': remaining_balance}}
            )
        
        flash('Car sold successfully', 'success')
        return redirect(url_for('cars.car_list'))
    
    return render_template('cars/sell_car.html', car=car, clients=clients)