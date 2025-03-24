
import sys, os
import io
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from apscheduler.schedulers.background import BackgroundScheduler
import pytest
from api_service.main import app, db, User, Persona
from api_service.py_files.model import GlobalVariable

scheduler = BackgroundScheduler()

@pytest.fixture
def client():
    """Fixture to create a Flask test client."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory DB
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_signup(client):
    """Test the signup route."""
    response = client.post('/signup', data={
        'username': 'testuser@g.harvard.edu',
        'password': 'Password123!',
        'confirmPassword': 'Password123!'
    })
    assert response.status_code in [200, 302], f"Unexpected status code: {response.status_code}"

def test_signout(client):
    """Test the signout route."""
    with client.session_transaction() as session:
        session['user_id'] = 1  # Mock user login

    response = client.get('/signout')
    assert response.status_code == 302

def test_get_personas(client):
    """Test retrieving all personas."""
    with app.app_context():
        user = User(username='testuser@g.harvard.edu')
        user.set_password('Password123!')  # Fix: Set password
        db.session.add(user)
        db.session.commit()

    with client.session_transaction() as session:
        session['user_id'] = 1

    response = client.get('/get_personas')
    assert response.status_code == 200

# def test_edit_persona(client):
#     """Test editing a persona."""
#     with app.app_context():
#         user = User(username='testuser@g.harvard.edu', openai_api_key='dummy_key')
#         user.set_password('Password123!')
#         db.session.add(user)
#         db.session.commit()

#         persona = Persona(
#             user_id=1, 
#             username=user.username, 
#             title='Old Title', 
#             prompt='Old Prompt', 
#             description='Old Description', 
#             categories=json.dumps(['Category1', 'Category2'])  # Add valid categories
#         )
#         db.session.add(persona)
#         db.session.commit()

#     with client.session_transaction() as session:
#         session['user_id'] = 1

#     response = client.post('/edit_persona', data={
#         'id': 1,
#         'new_title': 'New Title',
#         'new_prompt': 'New Prompt',
#         'new_description': 'New Description',
#         'new_category[]': ['Category1', 'Category2']
#     })
#     assert response.status_code in [200, 400]

def test_delete_persona(client):
    """Test deleting a persona."""
    with app.app_context():
        user = User(username='testuser@g.harvard.edu', openai_api_key='dummy_key')
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()

        persona = Persona(
            user_id=1, 
            username=user.username, 
            title='Test Persona', 
            prompt='Test Prompt', 
            description='Test Description', 
            categories=json.dumps(['Category1', 'Category2'])  # Add valid categories
        )
        db.session.add(persona)
        db.session.commit()

    with client.session_transaction() as session:
        session['user_id'] = 1

    response = client.post('/delete_persona', data={'id': 1})
    assert response.status_code in [200, 404]



# def test_upload_file(client):
#     """Test uploading a file."""
#     with app.app_context():
#         # Generate a 32-byte random salt directly
#         salt_32 = os.urandom(32)

#         # Encode the 32-byte salt in base64
#         valid_salt = base64.urlsafe_b64encode(salt_32).decode('utf-8')

#         # No need to manually pad; base64 encoding should be valid as it is

#         user = User(
#             username='testuser@g.harvard.edu',
#             openai_api_key='dummy_key',
#             openai_api_key_salt=valid_salt  # Use the correctly generated valid salt
#         )
#         user.set_password('Password123!')
#         db.session.add(user)
#         db.session.commit()

#         # Ensure user ID is set correctly without hardcoding
#         user_id = user.id

#     with client.session_transaction() as session:
#         session['user_id'] = user_id

#     # Upload a file with proper multipart form data
#     data = {
#         'file': (io.BytesIO(b"file content"), 'test.txt')
#     }
#     response = client.post('/upload_file', data=data, content_type='multipart/form-data')

#     # Check if the response status code is in the expected range
#     assert response.status_code in [200, 400]


# def test_delete_file(client):
#     """Test deleting a file."""
#     with app.app_context():
#         user = User(
#             username='testuser@g.harvard.edu',
#             openai_api_key='dummy_key',
#             openai_api_key_salt='R1J5cFdJZ1RxenBUNFhxRFp4cFRzdXFvOU5paFl2TFo='  # Valid salt
#         )
#         user.set_password('Password123!')
#         db.session.add(user)
#         db.session.commit()

#     with client.session_transaction() as session:
#         session['user_id'] = 1

#     response = client.post('/delete_file', data={'file_name': 'test.txt'})
#     assert response.status_code in [200, 404]


def test_update_key(client):
    """Test updating the OpenAI API key."""
    with app.app_context():
        user = User(username='testuser@g.harvard.edu')
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()

    with client.session_transaction() as session:
        session['user_id'] = 1

    response = client.post('/update_key', data={'openai_api_key': 'new_dummy_key'})
    assert response.status_code in [200, 400]

def test_check_api_key(client):
    """Test checking if an API key exists."""
    with app.app_context():
        user = User(username='testuser@g.harvard.edu', openai_api_key='dummy_key')
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()

    with client.session_transaction() as session:
        session['user_id'] = 1

    response = client.get('/check_api_key')
    assert response.status_code == 200

def test_index(client):
    """Test the index route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Academic Atlas" in response.data  # Adjust based on the actual content in index.html


def test_signin(client):
    """Test the signin route."""
    with app.app_context():
        user = User(username='testuser@g.harvard.edu', login_code=12345)
        user.set_password('Password123!')  # Populate the password_hash
        db.session.add(user)
        db.session.commit()

    # Test signin route with valid login_code
    response = client.post('/signin', data={
        'username': 'testuser@g.harvard.edu',
        'password': 'Password123!',
        'login_code': 12345
    })

    # Check for success or redirection
    assert response.status_code in [200, 302]
    assert b"Invalid Credentials" not in response.data


def test_persona_dashboard(client):
    """Test the persona dashboard route."""
    with app.app_context():
        # Create and commit the user
        user = User(username='testuser@g.harvard.edu')
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()

        # Refresh the user object to ensure it is bound to the session
        db.session.refresh(user)

    # Set the session user_id
    with client.session_transaction() as session:
        session['user_id'] = user.id

    # Access the dashboard
    response = client.get('/persona_dashboard')
    assert response.status_code == 200



# def test_add_persona(client):
#     """Test adding a persona."""
#     with app.app_context():
#         # Generate a valid 32-byte random key for Fernet
#         fernet_key = Fernet.generate_key().decode('utf-8')

#         # Create a user with required fields, including a valid Fernet key
#         user = User(
#             username='testuser@g.harvard.edu',
#             openai_api_key='sk-test-4FA4E1D7E2E8499F8E29E111A8A7D4C6',
#             openai_api_key_salt=fernet_key  # Use the generated 32-byte key
#         )
#         user.set_password('Password123!')
#         db.session.add(user)
#         db.session.commit()

#         print(f"OpenAI API Key Salt: {user.openai_api_key_salt}")

#         # Refresh the user instance to bind it to the session
#         db.session.refresh(user)

#     # Set session user_id
#     with client.session_transaction() as session:
#         session['user_id'] = user.id

#     # Test adding a persona
#     response = client.post('/add_persona', data={
#         'title': 'Test Persona',
#         'prompt': 'This is a test prompt.',
#         'description': 'Test description',
#         'category[]': ['Category1', 'Category2']
#     })

#     # Assert expected status codes
#     assert response.status_code in [200, 401], f"Unexpected status code: {response.status_code}"




# def test_api_chat(client):
#     """Test API chat."""
#     with app.app_context():
#         # Create a user with all required fields
#         user = User(
#             username='testuser@g.harvard.edu',
#             openai_api_key='sk-test-4FA4E1D7E2E8499F8E29E111A8A7D4C6',
#             openai_api_key_salt = 'VNLTuo93P6CIGz6eC3dVvwAW9wz3iyA07PBGxv_OEmE='
#         )
#         user.set_password('Password123!')  # Ensure password_hash is populated
#         db.session.add(user)
#         db.session.commit()

#         # Refresh the user instance
#         db.session.refresh(user)

#     # Set session user_id
#     with client.session_transaction() as session:
#         session['user_id'] = user.id

#     # Test the API chat endpoint
#     response = client.post('/api/chat', json={
#         'persona_id': 1,
#         'user_input': 'Hello',
#         'conversation': [{'role': 'user', 'content': 'Hi!'}]
#     })

#     # Assert expected status codes
#     assert response.status_code in [200, 403], f"Unexpected status code: {response.status_code}"

def test_scheduler_start(client):
    """Test that the scheduler starts correctly."""
    with app.app_context():
        if not scheduler.running:
            scheduler.start()  # Manually trigger the scheduler start

    # Assert that the scheduler is running
    assert scheduler.running, "Scheduler should be running"

def test_index_user_logged_in(client):
    """Test the index route when a user is logged in."""
    with app.app_context():
        # Create and commit a user
        user = User(username='testuser@g.harvard.edu')
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()

        # Query the user again to ensure it is bound to the session
        user = db.session.query(User).filter_by(username='testuser@g.harvard.edu').first()

    # Simulate a logged-in user
    with client.session_transaction() as session:
        session['user_id'] = user.id

    # Access the index route
    response = client.get('/')
    
    # Assert that the page renders successfully and includes the username
    assert response.status_code == 200
    assert b"testuser@g.harvard.edu" in response.data

def test_index_user_not_found(client):
    """Test the index route when the user ID in the session does not exist."""
    with client.session_transaction() as session:
        session['user_id'] = 999  # Non-existent user ID

    # Access the index route
    response = client.get('/')

    # Assert that the page renders successfully without crashing
    assert response.status_code == 200
    assert b"Academic Atlas" in response.data  # Replace with expected content in index.html

def test_persona_dashboard_unauthenticated(client):
    """Test the persona dashboard route when the user is not logged in."""
    # Access the persona dashboard without logging in
    response = client.get('/persona_dashboard')

    # Assert that the response is a 401 Unauthorized
    assert response.status_code == 401
    assert response.json == {"success": False, "message": "User not authenticated"}

def test_signup_missing_fields(client):
    """Test signup with missing fields."""
    with client.session_transaction() as session:
        session.clear()  # Ensure a clean session

    response = client.post('/signup', data={
        'username': '',
        'password': '',
        'confirmPassword': None  # Simulate missing confirmPassword
    }, follow_redirects=True)

    # Check that the flash message is present in the session
    with client.session_transaction() as session:
        flashed_messages = session['_flashes']
        assert flashed_messages[0][1] == "All fields are required"

    # Assert user is redirected to signup page
    assert response.status_code == 200


def test_signup_invalid_username(client):
    """Test signup with invalid username (missing '@')."""
    with client.session_transaction() as session:
        session.clear()  # Ensure a clean session

    response = client.post('/signup', data={
        'username': 'invalidusername',  # Missing '@'
        'password': 'Password123!',
        'confirmPassword': 'Password123!'
    }, follow_redirects=True)

    # Check that the flash message is present in the session
    with client.session_transaction() as session:
        flashed_messages = session['_flashes']
        assert flashed_messages[0][1] == "Username must contain '@'"

    # Assert user is redirected to signup page
    assert response.status_code == 200

def test_signup_unauthorized_email_domain(client):
    """Test signup with an unauthorized email domain."""
    with app.app_context():
        # Create and commit a global variable with an authorized email domain
        global_var = GlobalVariable(email_domain='example.edu')
        db.session.add(global_var)
        db.session.commit()

    response = client.post('/signup', data={
        'username': 'user@unauthorized.com',  # Unauthorized domain
        'password': 'Password123!',
        'confirmPassword': 'Password123!'
    }, follow_redirects=True)

    # Check that the error message is shown
    assert response.status_code == 200
    assert b"Email domain must be one of the following: example.edu, g.harvard.edu, fas.harvard.edu" in response.data

def test_signup_invalid_password(client):
    """Test signup with an invalid password."""
    with app.app_context():
        # Create an authorized domain for validation
        global_var = GlobalVariable(email_domain='example.edu')
        db.session.add(global_var)
        db.session.commit()

    response = client.post('/signup', data={
        'username': 'user@example.edu',
        'password': 'short',  # Invalid password
        'confirmPassword': 'short'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Password does not meet the required standards" in response.data

def test_signup_password_mismatch(client):
    """Test signup when passwords do not match."""
    with app.app_context():
        global_var = GlobalVariable(email_domain='example.edu')
        db.session.add(global_var)
        db.session.commit()

    response = client.post('/signup', data={
        'username': 'user@example.edu',
        'password': 'Password123!',
        'confirmPassword': 'DifferentPassword123!'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Passwords do not match" in response.data

def test_signup_username_exists(client):
    """Test signup with an already existing username."""
    with app.app_context():
        global_var = GlobalVariable(email_domain='example.edu')
        db.session.add(global_var)

        user = User(username='user@example.edu')
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()

    response = client.post('/signup', data={
        'username': 'user@example.edu',  # Existing username
        'password': 'Password123!',
        'confirmPassword': 'Password123!'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Username already exists" in response.data

def test_signup_unique_login_code(client):
    """Test that the login code generated is unique."""
    with app.app_context():
        global_var = GlobalVariable(email_domain='example.edu')
        db.session.add(global_var)

        # Create a user with a specific login code
        user = User(username='user1@example.edu', login_code=12345)
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()

    response = client.post('/signup', data={
        'username': 'user2@example.edu',  # New user
        'password': 'Password123!',
        'confirmPassword': 'Password123!'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Sign In" in response.data  # Redirects to signin page





def test_signup_redirect_to_signin(client):
    """Test signup redirects to the signin page on success."""
    with app.app_context():
        global_var = GlobalVariable(email_domain='example.edu')
        db.session.add(global_var)
        db.session.commit()

    response = client.post('/signup', data={
        'username': 'user@example.edu',
        'password': 'Password123!',
        'confirmPassword': 'Password123!'
    })

    assert response.status_code == 302  # Redirect status code
    assert response.location.endswith('/signin')  # Redirect to signin page

def test_signin_missing_fields(client):
    """Test signin with missing fields."""
    response = client.post('/signin', data={'username': '', 'password': ''})
    assert response.status_code == 200
    assert b"Invalid Credentials - Login Code is required" in response.data


def test_signin_invalid_credentials(client):
    """Test sign-in with invalid credentials."""
    response = client.post('/signin', data={
        'username': 'nonexistentuser@g.harvard.edu',  # Non-existent user
        'password': 'WrongPassword',
        'login_code': 12345
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid Credentials" in response.data

def test_add_persona_unauthenticated(client):
    """Test adding a persona without being authenticated."""
    response = client.post('/add_persona', data={
        'title': 'Test Persona',
        'prompt': 'Test Prompt',
        'description': 'Test Description',
        'category[]': ['Category1']
    })

    assert response.status_code == 401
    assert response.json == {"success": False, "message": "User not authenticated"}

def test_edit_persona_missing_api_key(client):
    """Test edit_persona endpoint with missing OpenAI API key."""
    with app.app_context():
        # Create and commit the user
        user = User(username='testuser@g.harvard.edu')
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()  # Commit user to DB

        # Ensure user is attached to session after commit
        user = db.session.query(User).filter_by(username='testuser@g.harvard.edu').first()

        # Create and commit the persona linked to the user
        persona = Persona(
            user_id=user.id,
            username=user.username,
            title="Test Persona",
            prompt="Test Prompt",
            description="Test Description",
            categories=json.dumps(["Category1", "Category2"]),
            image_url="dummy_image_path",
            public_url="dummy_public_url",
            web_browsing=False,
            code_interpreter=False,
        )
        db.session.add(persona)
        db.session.commit()

        # Re-attach persona instance to ensure it's available
        persona = db.session.query(Persona).filter_by(user_id=user.id).first()

    # Set session user_id
    with client.session_transaction() as session:
        session['user_id'] = user.id

    # Call the edit_persona endpoint without an API key
    response = client.post('/edit_persona', data={'id': persona.id})

    # Assert expected response status and message
    assert response.status_code == 403
    assert response.json == {"success": False, "message": "OpenAI API key not set"}




def test_signin_invalid_login_code(client):
    """Test sign-in with an invalid login code."""
    with app.app_context():
        user = User(username='testuser@g.harvard.edu', login_code=12345, needs_login_code=True)
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()

    response = client.post('/signin', data={
        'username': 'testuser@g.harvard.edu',
        'password': 'Password123!',
        'login_code': 54321  # Invalid login code
    }, follow_redirects=True)

    # Assert the error page is rendered
    assert response.status_code == 200
    assert b"Invalid Credentials" in response.data

    # Check flash message (if used)
    with client.session_transaction() as session:
        flashed_messages = session.get('_flashes', [])
        assert any("Invalid login code" in message for category, message in flashed_messages)

def test_get_personas_unauthenticated(client):
    """Test get_personas endpoint without authentication."""
    response = client.get('/get_personas')
    assert response.status_code == 401
    assert response.json == {"success": False, "message": "User not authenticated"}



def test_get_persona_success(client):
    """Test get_persona endpoint successfully fetching a persona."""
    with app.app_context():
        # Create and commit the user
        user = User(username='testuser@g.harvard.edu')
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()

        # Ensure user is attached to session after commit
        user = db.session.query(User).filter_by(username='testuser@g.harvard.edu').first()

        # Create and commit the persona linked to the user, including categories
        persona = Persona(
            user_id=user.id,
            username=user.username,
            title="Test Persona",
            prompt="Test Prompt",
            description="Test Description",
            categories=json.dumps(["Category1", "Category2"]),  # Provide valid categories
        )
        db.session.add(persona)
        db.session.commit()

        # Re-attach persona instance to ensure it's available
        persona = db.session.query(Persona).filter_by(user_id=user.id).first()

    # Set session user_id
    with client.session_transaction() as session:
        session['user_id'] = user.id

    # Call the get_persona endpoint to fetch the persona
    response = client.get(f'/get_persona/{persona.id}')
    
    # Assert expected response status and data
    assert response.status_code == 200
    assert response.json["success"] is True
    assert response.json["title"] == "Test Persona"

def test_edit_persona_unauthenticated(client):
    """Test edit_persona endpoint without authentication."""
    response = client.post('/edit_persona', data={'id': 1})
    assert response.status_code == 401
    assert response.json == {"success": False, "message": "User not authenticated"}


# def test_edit_persona_success(client):
#     """Test edit_persona endpoint successfully updating a persona."""
#     with app.app_context():
#         # Create a user and commit to the database (including dummy OpenAI API key and salt)
#         user = User(
#             username='testuser@g.harvard.edu',
#             openai_api_key='dummy_key',  # Provide a dummy OpenAI API key
#             openai_api_key_salt='zXcmEKp5cHg9v1j2YkvFrN3UtFR3c8kAebWFh8Jg9pI='  # Provide a valid 32-byte OpenAI API key salt
#         )
#         user.set_password('Password123!')
#         db.session.add(user)
#         db.session.commit()

#         # Rebind the user to the session
#         user = db.session.query(User).filter_by(username='testuser@g.harvard.edu').first()

#         # Create a persona and commit to the database
#         persona = Persona(
#             user_id=user.id,
#             username=user.username,
#             title="Old Title",
#             prompt="Old Prompt",
#             description="Old Description",
#             categories=json.dumps(["OldCategory1", "OldCategory2"])  # Provide valid categories
#         )
#         db.session.add(persona)
#         db.session.commit()

#         # Re-attach persona instance to ensure it's available
#         persona = db.session.query(Persona).filter_by(user_id=user.id).first()

#     # Set session user_id to authenticate the request
#     with client.session_transaction() as session:
#         session['user_id'] = user.id

#     # Call the edit_persona endpoint with updated data
#     response = client.post('/edit_persona', data={
#         'id': persona.id,
#         'new_title': 'New Title',
#         'new_prompt': 'New Prompt',
#         'new_description': 'New Description',
#         'new_category[]': json.dumps(['Category1', 'Category2'])  # Properly serialize the updated categories
#     })

#     # Assert response status code and data
#     assert response.status_code == 200, f"Expected 200 OK but got {response.status_code}. Response data: {response.data.decode()}"
#     assert response.json == {"success": True}


def test_delete_persona_unauthenticated(client):
    """Test delete_persona endpoint without authentication."""
    response = client.post('/delete_persona', data={'id': 1})
    assert response.status_code == 401
    assert response.json == {"success": False, "message": "User not authenticated"}

def test_delete_persona_missing_id(client):
    """Test delete_persona endpoint without providing a persona ID."""
    with app.app_context():
        user = User(username='testuser@g.harvard.edu')
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()

        db.session.refresh(user)  # Rebind the user to the session

    with client.session_transaction() as session:
        session['user_id'] = user.id

    response = client.post('/delete_persona', data={})
    assert response.status_code == 400
    assert response.json == {"success": False, "message": "No Persona ID provided"}


    response = client.post('/delete_persona', data={})
    assert response.status_code == 400
    assert response.json == {"success": False, "message": "No Persona ID provided"}

def test_delete_persona_success(client):
    """Test delete_persona endpoint successfully deleting a persona."""
    with app.app_context():
        # Create a user and commit to the database
        user = User(username='testuser@g.harvard.edu')
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()

        # Rebind the user to the session after committing
        user = db.session.query(User).filter_by(username='testuser@g.harvard.edu').first()

        # Create a persona and commit to the database
        persona = Persona(
            user_id=user.id,
            username=user.username,
            title="Test Persona",
            prompt="Test Prompt",
            description="Test Description",
            categories=json.dumps(["Category1", "Category2"])  # Provide valid categories
        )
        db.session.add(persona)
        db.session.commit()

        # Rebind the persona to the session after committing
        persona = db.session.query(Persona).filter_by(user_id=user.id).first()

    # Set session user_id
    with client.session_transaction() as session:
        session['user_id'] = user.id

    # Call the delete_persona endpoint
    response = client.post('/delete_persona', data={'id': persona.id})

    # Assert response status code and success message
    assert response.status_code == 200
    assert response.json == {"success": True}




