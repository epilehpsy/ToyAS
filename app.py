from flask import Flask, render_template, url_for, request, redirect
from models import db, User, logged_users, OAuth2Client
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from oauth2 import config_oauth, authorization
from authlib.oauth2 import OAuth2Error
import os
import time

login_manager = LoginManager()

def create_app(config_file=None):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['AUTHLIB_INSECURE_TRANSPORT'] = '1' #change this in production
    db.init_app(app)
    with app.app_context():
        db.create_all()

    login_manager.init_app(app)
    config_oauth(app)
    return app


app = create_app()


@login_manager.user_loader
def load_user(user_id):
    for user in logged_users:
        if user.id == int(user_id):
            return user

@app.route('/')
def index():
    return 'Hello, World!' +( current_user.username if current_user.is_authenticated  else "not logged in")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user:
        return "User already exists", 409
    
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()

    #Just to see if it works
    user = User.query.filter_by(username=username).first()
    return "User added successfully"+str(user.username),200


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return "Wrong username or password", 401
    
    login_user(user)
    logged_users.append(user)

    return redirect(url_for('me'))

# This is a protected route
@app.route('/me')
@login_required
def me():
    return render_template('me.html', clients=OAuth2Client.query.filter_by(user_id=current_user.id).all())

@app.route('/client_register', methods=['GET', 'POST'])
@login_required
def client_register():
    if request.method == 'GET':
        return render_template('client_register.html')

    name = request.form.get('name')
    #Client ID and Client Secret are generated automatically
    client_id =  os.urandom(24).hex()
    client_secret = os.urandom(24).hex()

    client = OAuth2Client(
        name=name,
        client_id=client_id,
        client_id_issued_at=int(time.time()),
        user_id=current_user.id,
    )

    client.client_secret = client_secret
    db.session.add(client)
    db.session.commit()
    return redirect(url_for('me'))



