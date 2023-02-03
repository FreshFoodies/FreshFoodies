from flask import Blueprint

receipt = Blueprint('receipt', __name__, template_folder='templates')

from . import views