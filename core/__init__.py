from flask import Flask
from config import Configuration
from datetime import datetime
import os
import json
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
app.url_map.strict_slashes = False
pymongo = PyMongo(app)

# blueprint for non-authentication parts of the app
from .food import food as food_blueprint
app.register_blueprint(food_blueprint)

from .receipt import receipt as receipt_blueprint
app.register_blueprint(receipt_blueprint)

from .models import Fridge, Food


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
"""
POST
EXPECTS:
{
    "email": "email",
    "slug": "name"
}

RETURNS:
{
    "_id":"",
    "foods":[...],
    "slug":"",
    "users":[...]
}
"""
@app.route("/api/fridge", methods=["POST"])
def new_fridge():
    raw_fridge = request.get_json()
    # raw_fridge["date_added"] = datetime.utcnow()
    fridge: Fridge = Fridge(**raw_fridge)
    fridge.foods = []
    fridge.slug = raw_fridge["slug"]
    fridge.users = [raw_fridge["email"]]
    insert_result = fridges.insert_one(fridge.to_bson())
    fridge.id = PydanticObjectId(str(insert_result.inserted_id))
    return fridge.to_json()

# Retrieve fridge from given ID
"""
Success: Returns JSON representation of Fridge
Failure: 404
"""
@app.route("/api/fridge/<string:id>", methods=["GET"])
def get_fridge(id):
    if len(id) != 24:
        flask.abort(404, "fridge not found")
    fridge = get_fridge_mongodb(id)
    return fridge.to_json()

# TODO: Update users of fridge
"""

"""
@app.route("/api/fridge/<string:id>/users", methods=["PUT"])
def update_fridge_users(id):
    pass


# TODO: Add or remove list of foods to fridge
"""
EXPECTS
{
    "foods": []
    "action": "add"/"remove"
}

slug field should be set to the food name with dashes in between
"""
@app.route("/api/fridge/<string:id>/foods", methods=["PUT"])
def add_to_fridge(id):
    request_json = request.get_json()
    action = request_json["action"]
    foods_raw = request_json["foods"]
    foods = json.loads(foods_raw)   # Parse food objects
    # filter = {'_id': PydanticObjectId(id)}  # Filter for finding fridge in database
    food_list = [Food(**food).to_bson() for food in foods]    # Convert JSON foods to food objects for mongodb
    if action == 'add':
        updated_fridge = fridges.find_one_and_update(
        {"_id": PydanticObjectId(id)},
        {"$push": {"foods": {"$each": food_list}}},
        return_document=ReturnDocument.AFTER,
        )
        if updated_fridge:  # Successfully added foods
            return food_list
        else:
            flask.abort(404, "Food not found")
    elif action == 'remove':
        pass
    else:
        flask.abort(400, "Invalid action")


# Get/modify information about a specific food in the fridge
"""
PUT EXPECTS
Food object

RETURNS
Food object: 
{
    "name": 
    "category":
    "location":
    ...
}
"""
@app.route("/api/fridge/<string:id>/foods/<string:slug>", methods=["GET", "PUT"])
def get_food(id, slug):
    fridge: Fridge = get_fridge_mongodb(id)
    foods = fridge.foods
    filtered_foods = list(filter(lambda x : x.slug == slug, foods))
    if request.method == "GET":
        return filtered_foods[0].to_json()
    elif request.method == "PUT":
        pass # Remove and reinsert food
    else:
        flask.abort(400, "Invalid request")


# Delete entire fridge
@app.route("/api/fridge/<string:id>", methods=["DELETE"])
def delete_food(id):
    id_object: PydanticObjectId = PydanticObjectId(id)
    deleted_fridge = fridges.find_one_and_delete(
        {"_id": id_object},
    )
    if deleted_fridge:
        return Fridge(**deleted_fridge).to_json()
    else:
        flask.abort(404, "Fridge not found")

# Retrieve fridge object
def get_fridge_mongodb(id) -> Fridge:
    id_object: PydanticObjectId = PydanticObjectId(id)
    raw_fridge = fridges.find_one_or_404(id_object)
    fridge: Fridge = Fridge(**raw_fridge)
    return fridge
