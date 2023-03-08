from flask import Flask, session, redirect
from config import Configuration
from datetime import datetime
import os
import bcrypt
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
app.secret_key = os.urandom(24)  # Secret key for client authentication
app.url_map.strict_slashes = False
pymongo = PyMongo(app)

# blueprint for non-authentication parts of the app
from .food import food as food_blueprint
app.register_blueprint(food_blueprint)

from .receipt import receipt as receipt_blueprint
app.register_blueprint(receipt_blueprint)

from .models import Fridge, Food, User

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
    return render_template('index.html', message=greeting)

"""
Create new user

{
    "name": "",
    "email": "",
    "password": ""
}

"""
@app.route("/api/signup", methods=["POST"])
def signup():
    message = ''
    # if "email" in session:
    #     return redirect(url_for("/api/logged_in"))
    if request.method == "POST":
        request_json = request.get_json()

        user = request_json["name"]
        email = request_json["email"]
        password = request_json["password"]

        user_found = users.find_one({"name": user})
        email_found = users.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index.html', message=message)
        else:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed, 'foods': [], 'fridge_ids': []}
            user: User = User(**user_input)
            users.insert_one(user.to_bson())
            
            user_data: User = get_user_mongodb(email)
            return user_data.to_json()
    return render_template('index.html')


"""
GET
EXPECTS:
{
    "email":
    "password":
}
"""
@app.route("/api/login", methods=["POST"])
def login():
    request_json = request.get_json()
    email = request_json["email"]
    # password = request_json["password"]
    user: User = get_user_mongodb(email)
    if user:
        return user.to_json()
    else:
        flask.abort(404, "User not found")

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
    fridge: Fridge = Fridge(**raw_fridge)
    fridge.foods = []
    email = raw_fridge["email"]
    fridge.slug = raw_fridge["slug"]
    fridge.users = [email]
    insert_result = fridges.insert_one(fridge.to_bson())
    fridge.id = PydanticObjectId(str(insert_result.inserted_id))

    # Add fridge ID to user's fridge_ids
    updated_user = users.find_one_and_update(
    {"email": email},
    {"$push": {"fridge_ids": fridge.id}},
    return_document=ReturnDocument.AFTER,
    )
    if updated_user:  # Successfully added foods
        print(f"Added ID to {email}'s account")
    else:
        print("User not found!")

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

# Add or remove user of fridge
"""
Expects 
{
    "email": "",
    "name": "",
    "action": "remove/add"
}

Returns email of user that was added to fridge
"""
@app.route("/api/fridge/<string:id>/users", methods=["PUT"])
def update_fridge_users(id):
    request_json = request.get_json()
    email = request_json["email"]
    # name = request_json["name"]
    action = request_json["action"]
    if action == "add":
        updated_fridge = fridges.find_one_and_update(
        {"_id": PydanticObjectId(id)},
        {"$push": {"users": email}},
        return_document=ReturnDocument.AFTER,
        )
        if updated_fridge:  # Successfully added user
            return email
        else:
            flask.abort(404, "Fridge not found")
    elif action == "remove":
        updated_fridge = fridges.find_one_and_update(
        {"_id": PydanticObjectId(id)},
        {"$pull": {"users": email}},
        return_document=ReturnDocument.AFTER,
        )
        if updated_fridge:  # Successfully removed user
            return email
        else:
            flask.abort(404, "Fridge not found")
    else:
        flask.abort(400, "Invalid action")

"""
EXPECTS
{
    "foods": [],
    "action": "add"/"remove",
    "reason": "eaten"/"wasted",
    "percentage": "x%"
}

Slug field should be set to the food name with dashes in between
If action == "remove",  pass in food names/slugs instead of entire food objects in the request body
"""
@app.route("/api/fridge/<string:id>/foods", methods=["PUT"])
def add_to_fridge(id):
    request_json = request.get_json()
    action = request_json["action"]
    foods_raw = request_json["foods"]
    foods = json.loads(foods_raw)   # Parse food objects
    if action == 'add':
        food_list = [Food(**food).to_bson() for food in foods]    # Convert JSON foods to food objects for mongodb
        updated_fridge = fridges.find_one_and_update(
        {"_id": PydanticObjectId(id)},
        {"$push": {"foods": {"$each": food_list}}},
        return_document=ReturnDocument.AFTER,
        )
        if updated_fridge:  # Successfully added foods
            return food_list
        else:
            flask.abort(404, "Fridge not found")
    elif action == 'remove':
        food_list = foods
        # Remove foods included in request body
        for slug in food_list:
            updated_fridge = fridges.find_one_and_update(
            {"_id": PydanticObjectId(id)},
            { "$pull": { "foods": { "slug": slug} } },
            return_document=ReturnDocument.AFTER,
            )
        if updated_fridge:  # Successfully removed foods
            return food_list
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
        # TODO: Remove and reinsert food
        print("replacing food")
        
    else:
        flask.abort(400, "Invalid request")


# Delete entire fridge
@app.route("/api/fridge/<string:id>", methods=["DELETE"])
def delete_food(id):
    id_object: PydanticObjectId = PydanticObjectId(id)
    deleted_fridge = fridges.find_one_and_delete(
        {"_id": id_object},
    )

    # TODO: allow deletion if user is the creater/user in the fridge

    if deleted_fridge:
        # Remove IDs from associated users
        fridge: Fridge = Fridge(**deleted_fridge)
        emails = fridge.users
        for email in emails:
            updated_fridge = users.find_one_and_update(
            {"email": email},
            {"$pull": {"fridge_ids": id_object}},
            return_document=ReturnDocument.AFTER,
            )
            if updated_fridge:  # Successfully removed user
                print(f"Removed fridge {id} from {email}'s account")
            else:
                print(f"No account found for {email}")
        return Fridge(**deleted_fridge).to_json()
    else:
        flask.abort(404, "Fridge not found")



# Retrieve fridge object reference from given ObjectId
def get_fridge_mongodb(id) -> Fridge:
    id_object: PydanticObjectId = PydanticObjectId(id)
    raw_fridge = fridges.find_one_or_404(id_object)
    fridge: Fridge = Fridge(**raw_fridge)
    return fridge

def get_user_mongodb(email: str) -> User:
    raw_user = users.find_one({"email": email})
    user: User = User(**raw_user)
    return user
