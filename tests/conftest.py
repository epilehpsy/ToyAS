from app import app, db
import pytest 

@pytest.fixture(scope='module')
def test_client():
    # Set the Testing configuration prior to creating the Flask application
    flask_app = app
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'


    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            print ("Using ", flask_app.config['SQLALCHEMY_DATABASE_URI'])
            yield testing_client  # this is where the testing happens!
            # Clean up after the testing is done
            db.drop_all()

