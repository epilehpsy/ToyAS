from models import OAuth2Client, OAuth2AuthorizationCode, OAuth2Token
username = 'test'
password = 'testpass'

client_name = 'test_client'
client_uris = 'http://localhost:5000/callback'

def test_index(test_client):
    response = test_client.get('/')
    assert response.status_code == 200  

def test_signup_page(test_client):
    response = test_client.get('/signup')
    assert response.status_code == 200

def test_signup_success(test_client):
    response = test_client.post('/signup', data=dict(username=username, password=password))
    assert response.status_code == 200

def test_signup_duplicate_user(test_client):
    response = test_client.post('/signup', data=dict(username=username, password=password))
    assert response.status_code == 409

def test_login_page(test_client):
    response = test_client.get('/login')
    assert response.status_code == 200

def test_me_forbidden(test_client):
    response = test_client.get('/me')
    assert response.status_code == 401

def test_login_success(test_client):
    response = test_client.post('/login', data=dict(username=username, password=password))
    assert response.status_code == 302

def test_login_failure(test_client):
    response = test_client.post('/login', data=dict(username=username, password='wrongpass'))
    assert response.status_code == 401

def test_me(test_client):
    response = test_client.get('/me')
    assert response.status_code == 200
    assert bytes(username, 'utf-8') in response.data

def test_client_register_page(test_client):
    response = test_client.get('/client_register')
    assert response.status_code == 200

def test_client_register(test_client):
    response = test_client.post('/client_register', data=dict(name=client_name, redirect_uris=client_uris))
    assert response.status_code == 302

def test_client_authorization_page(test_client):
    # Get the only client in the database
    oauthclient = OAuth2Client.query.first()
    print ("oauthclient")
    print(oauthclient.client_name)
    print(oauthclient.redirect_uris)
    response = test_client.get('/oauth/authorize?response_type=code&client_id='
                               +str(oauthclient.client_id)
                               +'&redirect_uri='+oauthclient.redirect_uris[0]
                               +'&scope=profile'
                               +'&state=xyz'
                            )
    
    print(response.data)
    assert response.status_code == 200
    assert bytes(client_name, 'utf-8') in response.data

def test_client_authorization_deny(test_client):
    oauthclient = OAuth2Client.query.first()
    print ("oauthclient")
    response = test_client.post('/oauth/authorize?response_type=code&client_id='
                               +str(oauthclient.client_id)
                               +'&redirect_uri='+oauthclient.redirect_uris[0]
                               +'&scope=profile'
                               +'&state=xyz',
                                data=dict(cancel="yes")
    )
    
    assert response.status_code == 302
    assert 'error=access_denied' in response.location


def test_client_authorization_confirm(test_client):
    # Get the only client in the database
    oauthclient = OAuth2Client.query.first()
    print ("oauthclient")
    response = test_client.post('/oauth/authorize?response_type=code&client_id='
                               +str(oauthclient.client_id)
                               +'&redirect_uri='+oauthclient.redirect_uris[0]
                               +'&scope=profile'
                               +'&state=xyz',
                                data=dict(confirm="yes")
    )
    
    print(response.location)
    print(response.data)
    assert response.status_code == 302
    assert 'code=' in response.location
    


def test_token(test_client):
    # Get the only client in the database
    oauthclient = OAuth2Client.query.first()
    authcode = OAuth2AuthorizationCode.query.filter_by(client_id=oauthclient.client_id).first().code

    print ("oauthclient")
    # client_secret on authorization header
    import base64
    response = test_client.post('/oauth/token',
                                headers={'Authorization': 'Basic ' + base64.b64encode(bytes(oauthclient.client_id+':'+oauthclient.client_secret, 'utf-8')).decode('utf-8')},
                                data=dict(grant_type='authorization_code',
                                            code=authcode,
                                            redirect_uri=oauthclient.redirect_uris[0]
                                )
    )
    print(response.data)    
    assert response.status_code == 200
    assert 'access_token' in response.json
    assert 'token_type' in response.json
    assert 'expires_in' in response.json

def test_api_profile(test_client):
    
    token = OAuth2Token.query.first().access_token
    response = test_client.get('/api/profile',
                                headers={'Authorization': 'Bearer ' + token}
    )
    print(response.data)
    assert response.status_code == 200
    assert bytes(username, 'utf-8') in response.data