from flask import Blueprint
from .models import Report

reports = Blueprint('reports', __name__, url_prefix="/reports")
