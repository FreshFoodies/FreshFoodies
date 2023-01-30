from flask import Flask
from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# blueprint for non-authentication parts of the app
from .add_food import food as food_blueprint
app.register_blueprint(food_blueprint)
from . import views
from core import views, models