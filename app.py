from flask import Flask, render_template, url_for, request
from models import db, User

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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user:
        return "User already exists"
    
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()

    #Just to see if it works
    user = User.query.filter_by(username=username).first()
    return f"User {user.username} added successfully"


