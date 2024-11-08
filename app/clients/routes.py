from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import mongo
from app.clients import bp
from bson.objectid import ObjectId
from datetime import datetime

@bp.route('/clients')
@login_required
def client_list():
    clients = mongo.db.clients.find()
    return render_template('clients/client_list.html', clients=clients)

@bp.route('/clients/add', methods=['GET', 'POST'])
@login_required
def add_client():
    if request.method == 'POST':
        client = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address')
        }
        mongo.db.clients.insert_one(client)
        flash('Client added successfully', 'success')
        return redirect(url_for('clients.client_list'))
    return render_template('clients/add_client.html')

@bp.route('/clients/edit/<client_id>', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):
    client = mongo.db.clients.find_one({'_id': ObjectId(client_id)})
    if request.method == 'POST':
        updated_client = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address')
        }
        mongo.db.clients.update_one({'_id': ObjectId(client_id)}, {'$set': updated_client})
        flash('Client updated successfully', 'success')
        return redirect(url_for('clients.client_list'))
    return render_template('clients/edit_client.html', client=client)

@bp.route('/clients/delete/<client_id>')
@login_required
def delete_client(client_id):
    mongo.db.clients.delete_one({'_id': ObjectId(client_id)})
    flash('Client deleted successfully', 'success')
    return redirect(url_for('clients.client_list'))

@bp.route('/clients/view/<client_id>')
@login_required
def view_client(client_id):
    client = mongo.db.clients.find_one({'_id': ObjectId(client_id)})
    cars = mongo.db.cars.find({'client_id': client_id})
    return render_template('clients/view_client.html', client=client, cars=cars)