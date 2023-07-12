username = 'test'
password = 'testpass'


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

def test_login_success(test_client):
    response = test_client.post('/login', data=dict(username=username, password=password))
    assert response.status_code == 200
    assert b"Logged in successfully" in response.data

def test_login_failure(test_client):
    response = test_client.post('/login', data=dict(username=username, password='wrongpass'))
    assert response.status_code == 401


