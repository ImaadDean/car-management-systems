from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import mongo
from app.expenses import bp
from bson.objectid import ObjectId
from datetime import datetime

@bp.route('/expenses')
@login_required
def expense_list():
    expenses = mongo.db.expenses.find()
    return render_template('expenses/expense_list.html', expenses=expenses)

@bp.route('/expenses/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        expense = {
            'date': datetime.strptime(request.form.get('date'), '%Y-%m-%d'),
            'amount': float(request.form.get('amount')),
            'category': request.form.get('category'),
            'description': request.form.get('description'),
            'car_id': request.form.get('car_id') if request.form.get('car_id') else None
        }
        mongo.db.expenses.insert_one(expense)
        flash('Expense added successfully', 'success')
        return redirect(url_for('expenses.expense_list'))
    cars = mongo.db.cars.find()
    return render_template('expenses/add_expense.html', cars=cars)

@bp.route('/expenses/edit/<expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    expense = mongo.db.expenses.find_one({'_id': ObjectId(expense_id)})
    if request.method == 'POST':
        updated_expense = {
            'date': datetime.strptime(request.form.get('date'), '%Y-%m-%d'),
            'amount': float(request.form.get('amount')),
            'category': request.form.get('category'),
            'description': request.form.get('description'),
            'car_id': request.form.get('car_id') if request.form.get('car_id') else None
        }
        mongo.db.expenses.update_one({'_id': ObjectId(expense_id)}, {'$set': updated_expense})
        flash('Expense updated successfully', 'success')
        return redirect(url_for('expenses.expense_list'))
    cars = mongo.db.cars.find()
    return render_template('expenses/edit_expense.html', expense=expense, cars=cars)

@bp.route('/expenses/delete/<expense_id>')
@login_required
def delete_expense(expense_id):
    mongo.db.expenses.delete_one({'_id': ObjectId(expense_id)})
    flash('Expense deleted successfully', 'success')
    return redirect(url_for('expenses.expense_list'))