from flask import Blueprint
from .models import Report

reports = Blueprint('reports', __name__, url_prefix="/reports")


"""
Expects:
{
    "email": _____
}
"""
@reports.route('/')
def index():
    return "hello"