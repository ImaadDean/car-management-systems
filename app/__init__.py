from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from flask_mail import Mail
from config import Config

mongo = PyMongo()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    mongo.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.cars import bp as cars_bp
    app.register_blueprint(cars_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.clients import bp as clients_bp
    app.register_blueprint(clients_bp, url_prefix='/clients')

    from app.expenses import bp as expenses_bp
    app.register_blueprint(expenses_bp, url_prefix='/expenses')
    from app.debt import bp as debt_bp
    app.register_blueprint(debt_bp, url_prefix='/debt')

    return app