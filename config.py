import os
from dotenv import load_dotenv 

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

class Configuration(object):
    # Environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')
    from urllib.parse import quote_plus
    username = quote_plus('Cluster83918')
    password = quote_plus('VGNVdn5IbWZz')
    MONGO_URI = "mongodb+srv://" + username + ":" + password + "@cluster83918.yxjnpr9.mongodb.net/?retryWrites=true&w=majority" #os.environ.get('MONGO_URI')
    