from flask import Blueprint

auto = Blueprint('auto',__name__)
from . import views
