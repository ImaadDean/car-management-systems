from flask import Blueprint

bp = Blueprint('cars', __name__)

from app.cars import routes