from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import mongo
from app.debt import bp
from bson.objectid import ObjectId
from datetime import datetime, timedelta

@bp.route('/')
@login_required
def debt_tracker():
    clients_with_debt = list(mongo.db.clients.find({"total_balance": {"$gt": 0}}))
    debts = list(mongo.db.debts.find())
    
    # Combine client information with their debts
    customers_with_debt = []
    for client in clients_with_debt:
        client_debts = [debt for debt in debts if debt['client_id'] == str(client['_id'])]
        customer_info = {
            '_id': client['_id'],
            'name': client['name'],
            'total_balance': client['total_balance'],
            'debts': client_debts
        }
        customers_with_debt.append(customer_info)
    
    return render_template('debt/debt_tracker.html', customers=customers_with_debt)

@bp.route('/<customer_id>')
@login_required
def customer_detail(customer_id):
    customer = mongo.db.customers.find_one({"_id": ObjectId(customer_id)})
    payments = list(mongo.db.payments.find({"customer_id": customer_id}).sort("payment_date", -1))
    return render_template('debt/customer_detail.html', customer=customer, payments=payments)

@bp.route('/<customer_id>/pay', methods=['POST'])
@login_required
def process_payment(customer_id):
    amount_paid = float(request.form.get('amount_paid'))
    customer = mongo.db.customers.find_one({"_id": ObjectId(customer_id)})
    
    if amount_paid <= 0 or amount_paid > customer['total_balance']:
        flash('Invalid payment amount', 'error')
        return redirect(url_for('debt.customer_detail', customer_id=customer_id))
    
    new_balance = customer['total_balance'] - amount_paid
    
    # Update customer's balance
    mongo.db.customers.update_one(
        {"_id": ObjectId(customer_id)},
        {
            "$set": {
                "total_balance": new_balance,
                "payment_plan.balance_due": new_balance
            },
            "$inc": {"payment_plan.installments_paid": 1}
        }
    )
    
    # Record the payment
    payment = {
        "customer_id": customer_id,
        "amount_paid": amount_paid,
        "payment_date": datetime.utcnow(),
        "remaining_balance": new_balance
    }
    mongo.db.payments.insert_one(payment)
    
    flash('Payment processed successfully', 'success')
    return redirect(url_for('debt.customer_detail', customer_id=customer_id))

@bp.route('/reminder', methods=['POST'])
@login_required
def toggle_reminder():
    customer_id = request.form.get('customer_id')
    reminder_status = request.form.get('reminder_status') == 'true'
    
    mongo.db.customers.update_one(
        {"_id": ObjectId(customer_id)},
        {"$set": {"reminder_enabled": reminder_status}}
    )
    
    status = "enabled" if reminder_status else "disabled"
    flash(f'Reminders {status} for the customer', 'success')
    return redirect(url_for('debt.debt_tracker'))

@bp.route('/<customer_id>/setup_plan', methods=['POST'])
@login_required
def setup_payment_plan(customer_id):
    total_amount = float(request.form.get('total_amount'))
    installment_amount = float(request.form.get('installment_amount'))
    frequency = request.form.get('frequency')
    start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')

    payment_plan = {
        "total_amount": total_amount,
        "installment_amount": installment_amount,
        "frequency": frequency,
        "start_date": start_date,
        "next_due_date": start_date,
        "balance_due": total_amount,
        "installments_paid": 0
    }

    mongo.db.customers.update_one(
        {"_id": ObjectId(customer_id)},
        {
            "$set": {
                "payment_plan": payment_plan,
                "total_balance": total_amount
            }
        }
    )

    flash('Payment plan set up successfully', 'success')
    return redirect(url_for('debt.customer_detail', customer_id=customer_id))