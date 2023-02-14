from flask import Flask
from config import Configuration
from datetime import datetime
import os

from pymongo.collection import Collection, ReturnDocument

import flask
from flask import Flask, request, url_for, jsonify, render_template
from flask_login import LoginManager
from flask_pymongo import PyMongo
from pymongo.errors import DuplicateKeyError

from .objectid import PydanticObjectId

# Set up flask app
app = Flask(__name__)
app.config.from_object(Configuration)
pymongo = PyMongo(app)

# blueprint for non-authentication parts of the app
from .food import food as food_blueprint
app.register_blueprint(food_blueprint)

from .receipt import receipt as receipt_blueprint
app.register_blueprint(receipt_blueprint)

from .models import Fridge


"""
Test Account and Fridge
"""
USER_ID = PydanticObjectId('63e374f9f538bd23252a2fd1')
FRIDGE_ID = PydanticObjectId('63e37436f538bd23252a2fcf')

# Get a reference to the fridge collection
fridges: Collection = pymongo.db.fridges
users: Collection = pymongo.db.users

@app.errorhandler(404)
def resource_not_found(e):
    """
    An error-handler to ensure that 404 errors are returned as JSON.
    """
    return jsonify(error=str(e)), 404


@app.errorhandler(DuplicateKeyError)
def resource_not_found(e):
    """
    An error-handler to ensure that MongoDB duplicate key errors are returned as JSON.
    """
    return jsonify(error=f"Duplicate key error."), 400

@app.route("/")
def index():
    greeting="Welcome to the LookingGlass API!"
    return render_template('index.html', greet=greeting)

# Create new empty fridge
@app.route("/fridge/new", methods=["POST"])
def new_fridge(id):
    raw_fridge = request.get_json()
    raw_fridge["date_added"] = datetime.utcnow()

    fridge: Fridge = Fridge(**raw_fridge)
    insert_result = fridges.insert_one(fridge.to_bson())
    fridge.id = PydanticObjectId(str(insert_result.inserted_id))
    return fridge.to_json()

# Retrieve fridge from given ID
"""
Success: Returns JSON representation of Fridge
Failure: 404
"""
@app.route("/fridge/<string:id>")
def get_fridge(id):
    if len(id) != 24:
        flask.abort(404, "fridge not found")
    id_object: PydanticObjectId = PydanticObjectId(id)
    raw_fridge = fridges.find_one_or_404(id_object)
    fridge: Fridge = Fridge(**raw_fridge)
    return fridge.to_json()

# TODO: Update users of fridge
"""

"""
@app.route("/fridge/<string:id>/users")
def update_fridge_users(id):
    pass


# TODO: Add or remove list of foods to fridge
"""
Expects a list of food names and:
"action": "add"/"remove"

slug field should be set to the food name with dashes in between
"""
@app.route("/fridge/<string:id>/foods/", methods=["PUT"])
def add_to_fridge(id):
    raw_food_list = request.get_json()
    count = None  # Store count to update fridge


# Get/modify information about a specifc food in the fridge
@app.route("/fridge/<string:id>/foods/<string:slug>", methods=["GET", "PUT"])
def get_food(id, slug):
    recipe = fridges.find_one_or_404({"slug": slug})
    return food(**recipe).to_json()


# Delete entire fridge
@app.route("/fridge/<string:id>", methods=["DELETE"])
def delete_food(id):
    id_object: PydanticObjectId = PydanticObjectId(id)
    deleted_fridge = fridges.find_one_and_delete(
        {"_id": id_object},
    )
    if deleted_fridge:
        return Fridge(**deleted_fridge).to_json()
    else:
        flask.abort(404, "fridge not found")


@app.route("/foods/<string:slug>", methods=["PUT"])
def update_food(slug):
    food = food(**request.get_json())
    food.date_updated = datetime.utcnow()
    updated_doc = fridges.find_one_and_update(
        {"slug": slug},
        {"$set": food.to_bson()},
        return_document=ReturnDocument.AFTER,
    )
    if updated_doc:
        return food(**updated_doc).to_json()
    else:
        flask.abort(404, "food not found")

