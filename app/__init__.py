from flask import Flask

app = Flask(__name__)

# Import routes so they register with the app
from app import routes
