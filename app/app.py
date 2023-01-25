from flask import Flask, jsonify, request, url_for
from user import get_current_user

app = Flask(__name__)

# Local accounts before we implement database
test_accounts = {'arjunsrivastava': {
    'first_name': 'Arjun',
    'last_name': 'Srivastava',
    'email': 'arj1@uw.edu',
    'current_fridge_items': 4
}}


@app.route("/")
def welcome():
    return "<p>Welcome to FreshFoodies!</p>"

# Get user information
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
    return {
        "username": user.username,
        "image": url_for("user_image", filename=user.image),
        'first_name': 'Arjun',
        'last_name': 'Srivastava',
        'email': 'arj1@uw.edu',
        'current_fridge_items': 4
    }