from flask import render_template, request, redirect, url_for
from flask_login import login_required
from app import mongo
from app.main import bp
from datetime import datetime, timedelta
from flask import flash

@bp.route('/')
@login_required
def dashboard():
    # Get current unsold cars
    unsold_cars = list(mongo.db.cars.find({'sold': False}))
    total_cars = len(unsold_cars)
    total_value = sum(float(car.get('price', 0)) for car in unsold_cars)
    
    # Calculate revenue (assuming it's the sum of all expenses)
    expenses = list(mongo.db.expenses.find())
    revenue = sum(float(expense.get('amount', 0)) for expense in expenses)
    
    # Calculate changes from last month
    one_month_ago = datetime.now() - timedelta(days=30)
    
    # New unsold cars in the last month
    new_cars_last_month = mongo.db.cars.count_documents({
        'created_at': {'$gte': one_month_ago},
        'sold': False
    })
    
    # Value increase percentage (for unsold cars)
    old_total_value = sum(float(car.get('price', 0)) for car in mongo.db.cars.find({
        'created_at': {'$lt': one_month_ago},
        'sold': False
    }))
    value_increase_percentage = ((total_value - old_total_value) / old_total_value * 100) if old_total_value else 0
    
    # Revenue increase percentage (unchanged as it's based on expenses)
    old_revenue = sum(float(expense.get('amount', 0)) for expense in mongo.db.expenses.find({'date': {'$lt': one_month_ago}}))
    revenue_increase_percentage = ((revenue - old_revenue) / old_revenue * 100) if old_revenue else 0

    def get_total_capital():
        capital = mongo.db.capital.find_one({})
        return capital['amount'] if capital else 0

    total_capital = get_total_capital()

    return render_template('main/dashboard.html', 
                           cars=unsold_cars, 
                           total_cars=total_cars, 
                           total_value=total_value, 
                           revenue=revenue,
                           new_cars_last_month=new_cars_last_month,
                           value_increase_percentage=value_increase_percentage,
                           revenue_increase_percentage=revenue_increase_percentage,
                           total_capital=total_capital)

@bp.route('/update_capital', methods=['POST'])
@login_required
def update_capital():
    new_capital = request.form.get('capital', type=float)
    if new_capital is not None:
        mongo.db.capital.update_one({}, {'$set': {'amount': new_capital}}, upsert=True)
        flash('Capital updated successfully', 'success')
    else:
        flash('Invalid capital amount', 'error')
    return redirect(url_for('main.dashboard'))