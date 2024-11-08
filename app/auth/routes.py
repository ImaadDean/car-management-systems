from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo
from app.models import User
from app.auth import bp
from app.auth.utils import send_confirmation_email
from app.auth.utils import serializer
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        existing_user = mongo.db.users.find_one({'$or': [{'username': username}, {'email': email}]})
        if existing_user is None:
            hashed_password = generate_password_hash(password)
            mongo.db.users.insert_one({'username': username, 'email': email, 'password': hashed_password, 'email_confirmed': False})
            send_confirmation_email(email)
            flash('Registration successful. Please check your email to confirm your account.')
            return redirect(url_for('auth.login'))
        flash('Username or email already exists')
    return render_template('auth/register.html')

@bp.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)  # Token expires after 1 hour
    except:
        flash('The confirmation link is invalid or has expired.')
        return redirect(url_for('auth.login'))
    
    user = mongo.db.users.find_one({'email': email})
    if user:
        mongo.db.users.update_one({'email': email}, {'$set': {'email_confirmed': True}})
        flash('Your email has been confirmed. You can now log in.')
    else:
        flash('User not found.')
    
    return redirect(url_for('auth.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = mongo.db.users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            if user.get('email_confirmed', False):
                login_user(User(user))
                return redirect(url_for('main.dashboard'))
            else:
                flash('Please confirm your email before logging in.')
        else:
            flash('Invalid username or password')
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))