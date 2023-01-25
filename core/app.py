import json
from flask import Flask, jsonify, request, url_for
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required, JWTManager
# from user import get_current_user

# NOTE: just a testing version of this function, should be imported from user.py
def get_current_user():
    return {
    'username': 'arjunsrivastava',   
    'first_name': 'Arjun',
    'last_name': 'Srivastava',
    'email': 'arj1@uw.edu',
    'current_fridge_items': 4
    }

app = Flask(__name__)

# Set up token keys
app.config["JWT_SECRET_KEY"] = "please-remember-to-change-me"
jwt = JWTManager(app)

# Local accounts before we implement database
test_accounts = {'arjunsrivastava': {
    'username': 'arjunsrivastava',
    'first_name': 'Arjun',
    'last_name': 'Srivastava',
    'email': 'arj1@uw.edu',
    'current_fridge_items': 4
}}


@app.route("/")
def welcome():
    return "<p>Welcome to FreshFoodies!</p>"

# Basic auth token
@app.route('/token', methods=["POST"])
def create_token():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    if email != "test" or password != "test":
        return {"msg": "Wrong email or password"}, 401

    access_token = create_access_token(identity=email)
    response = {"access_token":access_token}
    return response

# NOTE: MAY BE REDUNDANT Get user information
@app.route('/<username>', methods=['GET', 'POST'])
def login(username):
    if request.method == 'POST':
        user = get_current_user()
        if user.username != username: # Don't let users update other users' info
            return
        # update user data
        pass
    else:
        # NOTE: test account
        if username in test_accounts:
            return jsonify(test_accounts[username])

# Get my own profile
@app.route("/me")
def me_api():
    user = get_current_user()
    return user