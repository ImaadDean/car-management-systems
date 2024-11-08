from flask import Blueprint

bp = Blueprint('debt', __name__)

from app.debt import routes