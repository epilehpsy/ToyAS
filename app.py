from flask import Flask
from models import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# DB config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db.init_app(app)
#Create tables if they are not created yet
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return 'Hello, World!'

