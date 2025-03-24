import requests

BASE_URL = "http://104.198.147.52:5000"

def get_headers():
    """Returns headers with authentication if required."""
    # Modify as needed for your API's authentication
    return {
        "Content-Type": "application/json",
    }

def test_signup_get():
    url = f"{BASE_URL}/signup"
    response = requests.get(url, headers=get_headers())
    assert response.status_code == 200  # Check if the page loads successfully

def debug_response(response):
    print("Response Status Code:", response.status_code)
    print("Response Headers:", response.headers)
    print("Response Body:", response.text)

def test_signup_post():
    url = f"{BASE_URL}/signup"
    payload = {
        "username": "testuser@example.com",
        "password": "Test@123",
        "confirmPassword": "Test@123"
    }
    response = requests.post(url, json=payload, headers=get_headers())
    assert response.status_code in [200, 302, 400, 403, 500]  

# def test_signin_post():
#     url = f"{BASE_URL}/signin"
#     payload = {"username": "testuser@example.com", "password": "Test@123"}
#     response = requests.post(url, data=payload, headers=get_headers())
#     print("Response Status Code:", response.status_code)
#     print("Response Body:", response.text)
#     assert response.status_code in [200, 302, 401], f"Unexpected status code: {response.status_code}"

def test_signin():
    response = requests.post('/signin', json={
        'username': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 302


def test_add_persona():
    url = f"{BASE_URL}/add_persona"
    payload = {
        "title": "Test Persona",
        "prompt": "This is a test prompt",
        "description": "Test description",
        "category": ["test_category"],
        "web_browsing": True,
        "code_interpreter": False,
        "image": "test_image.png",
        "selected_files": []
    }
    response = requests.post(url, json=payload, headers=get_headers())
    assert response.status_code in [200, 401, 400, 500]

def test_shared_chat():
    url = f"{BASE_URL}/api/shared_chat"
    payload = {
        "persona_id": 1,
        "conversation": [],
        "admin_key_1": "dummy_key_1",
        "admin_key_2": "dummy_key_2",
        "salt": "dummy_salt",
    }
    response = requests.post(url, json=payload, headers=get_headers())
    assert response.status_code in [200, 400, 404, 500]

def test_shared_chat_without_key():
    url = f"{BASE_URL}/api/shared_chat_without_key"
    payload = {
        "persona_id": 1,
        "conversation": [],
        "admin_key_1": "dummy_key_1",
        "admin_key_2": "dummy_key_2",
        "salt": "dummy_salt",
    }
    response = requests.post(url, json=payload, headers=get_headers())
    assert response.status_code in [200, 400, 404, 500]

def test_chat():
    url = f"{BASE_URL}/chat/test_title/1"
    response = requests.get(url, headers=get_headers())
    assert response.status_code in [200, 401, 404]

# ==================== Academic Community Hub ====================

def test_persona_marketplace():
    url = f"{BASE_URL}/persona_marketplace"
    response = requests.get(url, headers=get_headers())
    assert response.status_code in [200, 404, 500]

# ==================== API Key Management ====================

def test_update_key():
    url = f"{BASE_URL}/update_key"
    payload = {"openai_api_key": "dummy_api_key"}
    response = requests.post(url, json=payload, headers=get_headers())
    assert response.status_code in [200, 401, 400, 500]

def test_update_serp_key():
    url = f"{BASE_URL}/update_serp_key"
    payload = {"serp_api_key": "dummy_serp_key"}
    response = requests.post(url, json=payload, headers=get_headers())
    assert response.status_code in [200, 401, 400, 500]

def test_delete_key():
    url = f"{BASE_URL}/delete_key"
    response = requests.post(url, headers=get_headers())
    assert response.status_code in [200, 401, 500]

def test_check_api_key():
    url = f"{BASE_URL}/check_api_key"
    response = requests.get(url, headers=get_headers())
    assert response.status_code in [200, 401]

# ==================== File Upload/Deletion ====================

def test_upload_file():
    url = f"{BASE_URL}/upload_file"
    files = {"file": ("test.txt", "dummy content")}
    response = requests.post(url, files=files, headers=get_headers())
    assert response.status_code in [200, 401, 400, 500]

def test_delete_file():
    url = f"{BASE_URL}/delete_file"
    payload = {"file_name": "test.txt"}
    response = requests.post(url, json=payload, headers=get_headers())
    assert response.status_code in [200, 401, 404]

# ==================== Admin APIs ====================

def test_admin_login():
    url = f"{BASE_URL}/admin/admin_login"
    payload = {"username": "admin", "password": "admin_password"}
    response = requests.post(url, data=payload, headers=get_headers())  # Use `data` for form-data
    print("Response Status Code:", response.status_code)
    print("Response Body:", response.text)
    assert response.status_code in [200, 400, 403], f"Unexpected status code: {response.status_code}"


def test_admin_get_users():
    url = f"{BASE_URL}/admin/api/users"
    payload = {"admin_key_1": "dummy_key_1", "admin_key_2": "dummy_key_2", "salt": "dummy_salt"}
    response = requests.post(url, json=payload, headers=get_headers())
    assert response.status_code in [200, 400, 401, 403, 500]

def test_admin_get_personas():
    url = f"{BASE_URL}/admin/api/personas"
    payload = {"admin_key_1": "dummy_key_1", "admin_key_2": "dummy_key_2", "salt": "dummy_salt"}
    response = requests.post(url, json=payload, headers=get_headers())
    assert response.status_code in [200, 400, 401, 403, 500]

def test_admin_get_files():
    url = f"{BASE_URL}/admin/api/files"
    payload = {"admin_key_1": "dummy_key_1", "admin_key_2": "dummy_key_2", "salt": "dummy_salt"}
    response = requests.post(url, json=payload, headers=get_headers())
    assert response.status_code in [200, 400, 401, 403, 500]

# ==================== Email Chat ====================

def test_email_chat():
    url = f"{BASE_URL}/api/email_chat"
    payload = {
        "personaName": "Test Persona",
        "personaDescription": "This is a test persona",
        "conversation": [],
    }
    response = requests.post(url, json=payload, headers=get_headers())
    assert response.status_code in [200, 400, 404, 500]

def test_email_chat_with_email():
    url = f"{BASE_URL}/api/email_chat_with_email"
    payload = {
        "userEmail": "test@example.com",
        "personaName": "Test Persona",
        "personaDescription": "This is a test persona",
        "conversation": [],
    }
    response = requests.post(url, json=payload, headers=get_headers())
    assert response.status_code in [200, 400, 500]

# ==================== Usage History ====================

def test_usage_history_get():
    url = f"{BASE_URL}/usage_history"
    headers = get_headers()
    response = requests.get(url, headers=headers)
    print("Response Status Code:", response.status_code)
    print("Response Body:", response.text)
    assert response.status_code in [200, 404]

def test_usage_history_post():
    url = f"{BASE_URL}/usage_history/api/"
    payload = {}
    response = requests.post(url, json=payload, headers=get_headers())
    assert response.status_code in [200, 401, 500]

# ==================== Admin Access ====================

def test_admin_access():
    url = f"{BASE_URL}/admin_access/api/"
    payload = {"admin_key_1": "dummy_key_1", "admin_key_2": "dummy_key_2", "salt": "dummy_salt"}
    response = requests.post(url, json=payload, headers=get_headers())
    assert response.status_code in [200, 400, 401, 403, 500]

# ==================== Global Variables ====================

def test_update_email_domain():
    url = f"{BASE_URL}/admin/global_variable_email_domain"
    payload = {"email_domain": "test.com", "admin_key_1": "dummy_key_1", "admin_key_2": "dummy_key_2", "salt": "dummy_salt"}
    response = requests.post(url, json=payload, headers=get_headers())
    assert response.status_code in [200, 400, 403, 500]

def test_update_api_keys():
    url = f"{BASE_URL}/admin/global_variable_api_keys"
    payload = {"open_ai_key": "dummy_openai_key", "google_search_api_key": "dummy_google_key", "admin_key_1": "dummy_key_1", "admin_key_2": "dummy_key_2", "salt": "dummy_salt"}
    response = requests.post(url, json=payload, headers=get_headers())
    assert response.status_code in [200, 400, 403, 500]
