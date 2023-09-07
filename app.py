from flask import Flask, render_template, url_for, request, redirect, jsonify, send_from_directory, flash, send_file
from models import db, User, logged_users, OAuth2Client, Image
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from oauth2 import config_oauth, authorization, require_oauth
from authlib.oauth2 import OAuth2Error
import os, io
import time
import json
from authlib.integrations.flask_oauth2 import current_token
import base64
import vuln_protection_config

login_manager = LoginManager()

def initialize_table(app):
    user = User(id=0, username='testuser', password='testpass')
    db.session.add(user)
    client = OAuth2Client(
                client_id='demo-client-id',
                client_id_issued_at=int(time.time()),
                user_id=user.id,
            )

    client_metadata = {
                "client_name": 'test-client-name',
                "redirect_uris":['http://127.0.0.1:5000/callback', 'http://127.0.0.1:5000/click_callback'],
                "scope": "profile images",
                "grant_types": ["authorization_code"], # For the token endpoint
                "response_types": ["code"] # For the authorization endpoint
            }

    client.set_client_metadata(client_metadata)
    client.client_secret = 'demo-client-secret'
    db.session.add(client)
    db.session.commit()


def create_app(config_file=None):
    app = Flask(__name__)
    app.config.from_pyfile('defaultconf.cfg')
    os.environ['AUTHLIB_INSECURE_TRANSPORT'] = '1'
    db.init_app(app)
    with app.app_context():
        db.create_all()
        if len(db.session.query(User).all()) == 0:
            initialize_table(app)

    login_manager.login_view = "login"
    login_manager.init_app(app)
    config_oauth(app)
    return app


app = create_app()

@app.template_filter('b64encode')
def b64encode(s):
    return base64.b64encode(s).decode('utf-8')

# static resources
@app.route('/static/<path:path>')
def static_file(path):
    return send_from_directory('static', path)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return  render_template('index.html')

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
    #login_user(user)
    flash("Registered successfully!")
    return redirect(url_for('login'))


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
    # if user is not just to log in, but need to head back to the auth page, then go for it
    next_page = request.args.get('next')
    if next_page:
        return redirect(next_page)
    flash('Welcome back '+user.username)
    return redirect(url_for('me'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# This is a protected route
@app.route('/me')
@login_required
def me():
    return render_template('me.html', user=User.query.filter_by(id = current_user.id), clients=OAuth2Client.query.filter_by(user_id=current_user.id).all())

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
        client_id=client_id,
        client_id_issued_at=int(time.time()),
        user_id=current_user.id,
    )

    client_metadata = {
        "client_name": name,
        "redirect_uris": request.form.get('redirect_uris').splitlines(),
        "scope": "profile images",
        "grant_types": ["authorization_code"], # For the token endpoint
        "response_types": ["code"] # For the authorization endpoint
    }

    client.set_client_metadata(client_metadata)
    client.client_secret = client_secret
    db.session.add(client)
    db.session.commit()
    flash('Client added successfully')
    return redirect(url_for('me'))


@app.route('/images', methods=['GET', 'POST'])
@login_required
def images():
    if request.method == 'GET':
        user_images=Image.query.filter_by(user_id=current_user.id).all()
        return render_template('images.html', images=user_images)

    #TODO: Add image 
    image = request.files.get('image')
    if not image:
        return "No image", 400
    
    # save the image to the database
    image = Image(
        user_id=current_user.id,
        name=image.filename,
        img=image.read(),
    )
    db.session.add(image)
    db.session.commit()
    flash('Image added successfully')
    return redirect(url_for('images'))

@app.route('/images/<int:image_id>/download')
@login_required
def download_image(image_id):
    image = Image.query.filter_by(id=image_id).first()

    if not image or image.user_id != current_user.id:
        return "Image not found", 404

    if request.method == 'GET':
        return send_file(io.BytesIO(image.img), download_name=image.name, mimetype='image/jpg')

@app.route('/images/<int:image_id>/delete')
@login_required
def delete_image(image_id):
    image = Image.query.filter_by(id=image_id).first()

    if not image or image.user_id != current_user.id:
        return "Image not found", 404

    db.session.delete(image)
    db.session.commit()
    flash('Image deleted successfully')
    return redirect(url_for('images'))






## API PART

@app.route('/oauth/authorize', methods=['GET', 'POST'])
@login_required
def authorize():

    if request.method == 'POST':
        grant_user = None
        if request.form.get('confirm'):
            grant_user = current_user
        return authorization.create_authorization_response(grant_user=grant_user)
            
    try:
        grant = authorization.get_consent_grant(end_user=current_user)
        if vuln_protection_config.CLICKJACKING:
            return render_template('authorize.html', grant=grant) , 200, {'X-Frame-Options': 'DENY'}
        else:
            return render_template('authorize.html', grant=grant)

    except OAuth2Error as error:
        return error.get_body() , error.status_code

@app.route('/oauth/token', methods=['POST'])
def token():
    return authorization.create_token_response()


@app.route('/api/profile')
@require_oauth('profile')
def api_profile():
    user = current_token.user
    return jsonify(id=user.id, username=user.username)

@app.route('/api/images', methods=['GET', 'POST'])
@require_oauth('images')
def api_images():
    user = current_token.user
    if request.method == 'GET':
        images = Image.query.filter_by(user_id=user.id).all()
        return jsonify([{'id': image.id, 'name': image.name} for image in images])
    
    image = request.files.get('image')
    if not image:
        return "No image", 400
    
    # save the image to the database
    image = Image(
        user_id=user.id,
        name=image.filename,
        img=image.read(),
    )
    db.session.add(image)
    db.session.commit()
    return "Image added successfully", 201, {'Location': url_for('api_image', image_id=image.id)}

@app.route('/api/images/<int:image_id>')
@require_oauth('images')
def api_image(image_id):
    user = current_token.user
    image = Image.query.filter_by(id=image_id, user_id=user.id).first()
    if not image:
        return "Image not found", 404
    return b64encode(image.img)


