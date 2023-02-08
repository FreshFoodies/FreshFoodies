from flask import Flask
from config import Configuration
from datetime import datetime
import os

from pymongo.collection import Collection, ReturnDocument

import flask
from flask import Flask, request, url_for, jsonify, render_template
from flask_pymongo import PyMongo
from pymongo.errors import DuplicateKeyError

from .models import Fridge, User, Food
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


"""
Test Account and Fridge
"""
USER_ID = PydanticObjectId('63e374f9f538bd23252a2fd1')

# Get a reference to the fridge collection
fridges: Collection = pymongo.db.fridges

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
    greeting="Hello there"
    return render_template('index.html', greet=greeting)

@app.route("/fridge/")
# def list_foods():
#     """
#     GET a list of current foods in user's fridge
#     The results are paginated using the `page` parameter.
#     """

#     page = int(request.args.get("page", 1))
#     per_page = 10  # A const value.



#     # For pagination, it's necessary to sort by name,
#     # then skip the number of docs that earlier pages would have displayed,
#     # and then to limit to the fixed page size, ``per_page``.
#     cursor = fridges.find().sort("slug").skip(per_page * (page - 1)).limit(per_page)

#     food_count = fridges.count_documents({})

#     links = {
#         "self": {"href": url_for(".list_foods", page=page, _external=True)},
#         "last": {
#             "href": url_for(
#                 ".list_foods", page=(food_count // per_page) + 1, _external=True
#             )
#         },
#     }
#     # Add a 'prev' link if it's not on the first page:
#     if page > 1:
#         links["prev"] = {
#             "href": url_for(".list_foods", page=page - 1, _external=True)
#         }
#     # Add a 'next' link if it's not on the last page:
#     if page - 1 < food_count // per_page:
#         links["next"] = {
#             "href": url_for(".list_foods", page=page + 1, _external=True)
#         }

#     return {
#         "fridges": [food(**doc).to_json() for doc in cursor],
#         "_links": links,
#     }
def list_fridge():
    fridge = fridges.find_one(PydanticObjectId('63e37436f538bd23252a2fcf'))
    print(fridge)
    return "success"

@app.route("/foods/", methods=["POST"])
def new_food():
    raw_food = request.get_json()
    raw_food["date_added"] = datetime.utcnow()

    food = food(**raw_food)
    insert_result = fridges.insert_one(food.to_bson())
    food.id = PydanticObjectId(str(insert_result.inserted_id))
    print(food)

    return food.to_json()


@app.route("/foods/<string:slug>", methods=["GET"])
def get_food(slug):
    recipe = fridges.find_one_or_404({"slug": slug})
    return food(**recipe).to_json()


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


@app.route("/foods/<string:slug>", methods=["DELETE"])
def delete_food(slug):
    deleted_food = fridges.find_one_and_delete(
        {"slug": slug},
    )
    if deleted_food:
        return food(**deleted_food).to_json()
    else:
        flask.abort(404, "food not found")