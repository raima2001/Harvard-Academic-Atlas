# API Documentation

## Base URL
`http://104.198.147.52:5000`

### Safety Measures in API Design

This API is designed with multiple safety measures to ensure secure and reliable access, authentication, and data handling:

#### **1. Cross-Origin Resource Sharing (CORS) Configuration**
The API employs a restrictive CORS policy to allow requests only from trusted origins, thereby mitigating risks of unauthorized cross-origin requests. This is configured as follows:
```python
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5000",
    "http://104.198.147.52:5000"
]

cors = CORS(app, resources={r"/*": {"origins": CORS_ALLOWED_ORIGINS}})
```
- **Purpose**: Restricts API access to pre-approved client applications only.
- **Benefit**: Reduces exposure to malicious scripts running from unauthorized domains.

---

#### **2. User Authentication and Session Management**
- **Authentication**: The API uses `user_id` stored in the session to verify that requests are made by authenticated users.
- **Enforcement**: Endpoints that require authentication check the `user_id` before proceeding:
  ```python
  user_id = session.get('user_id')
  if not user_id:
      return jsonify(success=False, message="User not authenticated"), 401
  ```
- **Purpose**: Prevents unauthorized access by ensuring that only logged-in users can interact with secure endpoints.
- **Benefit**: Protects user-specific data from being accessed by unauthenticated or malicious actors.

---

#### **3. Input Validation**
- Input data, such as email domains, API keys, and user credentials, are validated to ensure compliance with expected formats and requirements:
  - Email domains are checked against an authorized list.
  - Passwords are validated for strength and match confirmation.
  - API keys are validated against third-party services before storing them securely.

---

#### **4. Data Encryption**
- Sensitive data, such as API keys and user credentials, is encrypted using cryptographic libraries (e.g., `Fernet` for symmetric encryption).
- Encryption keys are securely managed, ensuring that only authorized parties can decrypt the stored data.

---

#### **5. Role-Based Access Control**
- Specific endpoints (e.g., admin endpoints) enforce additional layers of authentication by verifying encrypted admin credentials.
- Regular users cannot access administrative features or manipulate sensitive data.

---

#### **6. Error Handling and Logging**
- Errors are handled gracefully, and detailed error messages are logged for debugging while limiting information exposure to the client:
  ```python
  except Exception as e:
      return jsonify(error=f"An unexpected error occurred: {str(e)}"), 500
  ```
- **Purpose**: Prevents sensitive data leakage in error messages.

---

#### **8. Secure File Uploads**
- Uploaded files are validated for type and content before processing.
- Filenames are sanitized, and existing files are overwritten securely.

---

# **Endpoints**

### Signup
- **Endpoint**: `/signup`
- **Method**: `GET, POST`
- **Description**: Allows new users to create an account.
- **Request Body** (POST):
  - `username`: Email address of the user.
  - `password`: User's password.
  - `confirmPassword`: Password confirmation.
- **Responses**:
  - `200 OK`: Renders the signup page.
  - `302 Redirect`: Redirects to `signin` on successful signup.
  - `400/403/500`: Error during signup.

---

### Signin
- **Endpoint**: `/signin`
- **Method**: `GET, POST`
- **Description**: Authenticates users.
- **Request Body** (POST):
  - `username`: User's email.
  - `password`: User's password.
  - `login_code`: Optional, for first-time login.
- **Responses**:
  - `200 OK`: Renders the signin page.
  - `302 Redirect`: Redirects to the homepage on successful login.
  - `401 Unauthorized`: Invalid credentials.

---

### Signout
- **Endpoint**: `/signout`
- **Method**: `GET`
- **Description**: Logs out the user.
- **Responses**:
  - `302 Redirect`: Redirects to the homepage.

---

### Academic Bot Builder Dashboard
- **Endpoint**: `/persona_dashboard`
- **Method**: `GET`
- **Description**: Displays the Academic Bot Builder dashboard for the authenticated user.
- **Responses**:
  - `200 OK`: Renders the Academic Bot Builder dashboard.
  - `401 Unauthorized`: User not authenticated.

---

### Add Academic Bot
- **Endpoint**: `/add_persona`
- **Method**: `POST`
- **Description**: Adds a new Academic Bot for the authenticated user.
- **Request Body**:
  - `title`, `prompt`, `description`, `category[]`, `web_browsing`, `code_interpreter`, `image`, `selected_files`.
- **Responses**:
  - `200 OK`: Academic Bot added successfully.
  - `401 Unauthorized`: User not authenticated.
  - `400/500`: Error during Academic Bot creation.

---

### Get Academic Bot
- **Endpoint**: `/get_personas`
- **Method**: `GET`
- **Description**: Retrieves all Academic Bot for the authenticated user.
- **Responses**:
  - `200 OK`: List of Academic Bot.
  - `401 Unauthorized`: User not authenticated.

---

### Get Academic Bot
- **Endpoint**: `/get_persona/<int:persona_id>`
- **Method**: `GET`
- **Description**: Retrieves details of a specific Academic Bot.
- **Responses**:
  - `200 OK`: Academic Bot details.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: Academic Bot not found.

---

### Edit Academic Bot
- **Endpoint**: `/edit_persona`
- **Method**: `POST`
- **Description**: Updates an existing Academic Bot.
- **Request Body**:
  - `id`, `new_title`, `new_prompt`, `new_description`, `new_category[]`, `new_image`, `web_browsing`, `code_interpreter`, `retrieval_toggle`, `selected_files`.
- **Responses**:
  - `200 OK`: Academic Bot updated successfully.
  - `401 Unauthorized`: User not authenticated.
  - `404/500`: Error during Academic Bot update.

---

### Delete Academic Bot
- **Endpoint**: `/delete_persona`
- **Method**: `POST`
- **Description**: Deletes a Academic Bot.
- **Request Body**:
  - `id`: Academic Bot ID.
- **Responses**:
  - `200 OK`: Academic Bot deleted successfully.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: Academic Bot not found.
 
---

### Get Academic Bot Public URL
- **Endpoint**: `/get_persona_public_url/<int:persona_id>`
- **Method**: `GET`
- **Description**: Retrieves the public URL of an Academic Bot.
- **Responses**:
  - `200 OK`: Public URL.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: Academic Bot not found.

---

### Toggle Public Academic Bot
- **Endpoint**: `/toggle_public_persona`
- **Method**: `POST`
- **Description**: Updates the public status of an Academic Bot.
- **Request Body**:
  - `persona_id`: ID of the Academic Bot.
  - `make_public`: Public status (`true`, `false`, or `yes_without_key`).
- **Responses**:
  - `200 OK`: Academic Bot public status updated successfully.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: Academic Bot not found.
  - `400/500`: Error during update.

---

### Share Academic Bot
- **Endpoint**: `/share/<persona_hash>/<persona_name>`
- **Method**: `GET`
- **Description**: Displays a shared Academic Bot chat interface.
- **Responses**:
  - `200 OK`: Academic Bot chat rendered.
  - `404 Not Found`: Academic Bot not found or not public.
  - `500 Internal Server Error`: Error during rendering.

---

### Shared Chat API
- **Endpoint**: `/api/shared_chat`
- **Method**: `POST`
- **Description**: Handles chat interactions for shared Academic Bot requiring keys.
- **Request Body**:
  - `persona_id`: ID of the Academic Bot.
  - `conversation`: Conversation history.
  - `admin_key_1`: Encrypted admin key part 1.
  - `admin_key_2`: Encrypted admin key part 2.
  - `salt`: Encryption salt.
- **Responses**:
  - `200 OK`: Chat response.
  - `400/404/500`: Various errors.

---

### Shared Chat Without Key API
- **Endpoint**: `/api/shared_chat_without_key`
- **Method**: `POST`
- **Description**: Handles chat interactions for shared Academic Bot not requiring keys.
- **Request Body**:
  - `persona_id`: ID of the Academic Bot.
  - `conversation`: Conversation history.
  - `admin_key_1`: Encrypted admin key part 1.
  - `admin_key_2`: Encrypted admin key part 2.
  - `salt`: Encryption salt.
- **Responses**:
  - `200 OK`: Chat response.
  - `400/404/500`: Various errors.

---

### Chat
- **Endpoint**: `/chat/<persona_title>/<int:persona_id>`
- **Method**: `GET`
- **Description**: Opens a chat interface for a specific Academic Bot.
- **Responses**:
  - `200 OK`: Chat interface.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: Academic Bot not found.

---

### API Chat
- **Endpoint**: `/api/chat`
- **Method**: `POST`
- **Description**: Handles chat interactions with Academic Bot.
- **Request Body**:
  - `persona_id`: Academic Bot ID.
  - `user_input`: User message.
  - `conversation`: Conversation history.
- **Responses**:
  - `200 OK`: Chat response.
  - `401 Unauthorized`: User not authenticated.
  - `500 Internal Server Error`: Chat error.

---

### Academic Community Hub
- **Endpoint**: `/persona_marketplace`
- **Method**: `GET`
- **Description**: Displays the public Academic Community Hub.
- **Responses**:
  - `200 OK`: Academic Community Hub rendered.
  - `404 Not Found`: User not logged in.
  - `500 Internal Server Error`: Error during rendering.

---

### Update API Key
- **Endpoint**: `/update_key`
- **Method**: `POST`
- **Description**: Updates the user's OpenAI API key.
- **Request Body**:
  - `openai_api_key`.
- **Responses**:
  - `200 OK`: API key updated.
  - `401 Unauthorized`: User not authenticated.
  - `400/500`: Error during update.

---

### Update SERP Key
- **Endpoint**: `/update_serp_key`
- **Method**: `POST`
- **Description**: Updates the user's Google Custom Search API key.
- **Request Body**:
  - `serp_api_key`.
- **Responses**:
  - `200 OK`: Key updated.
  - `401 Unauthorized`: User not authenticated.
  - `400/500`: Error during update.

---

### Delete API Key
- **Endpoint**: `/delete_key`
- **Method**: `POST`
- **Description**: Deletes the user's OpenAI API key.
- **Responses**:
  - `200 OK`: Key deleted.
  - `401 Unauthorized`: User not authenticated.
  - `500 Internal Server Error`: Error during deletion.

---

### Check API Key
- **Endpoint**: `/check_api_key`
- **Method**: `GET`
- **Description**: Checks if the user has an OpenAI API key.
- **Responses**:
  - `200 OK`: API key status.
  - `401 Unauthorized`: User not authenticated.

---

### Upload File
- **Endpoint**: `/upload_file`
- **Method**: `POST`
- **Description**: Uploads a file to the user's Resource Vault.
- **Request Body**:
  - `file`: File to upload.
- **Responses**:
  - `200 OK`: File uploaded successfully.
  - `401 Unauthorized`: User not authenticated.
  - `400/500`: Error during file upload.

---

### Delete File
- **Endpoint**: `/delete_file`
- **Method**: `POST`
- **Description**: Deletes a file from the user's Resource Vault.
- **Request Body**:
  - `file_name`: Name of the file to delete.
- **Responses**:
  - `200 OK`: File deleted successfully.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: File not found.

---

### Admin Login
- **Endpoint**: `/admin/login`
- **Method**: `GET, POST`
- **Description**: Logs in as an admin.
- **Request Body** (POST):
  - `username`: Admin username.
  - `password`: Admin password.
- **Responses**:
  - `200 OK`: Admin panel rendered.
  - `400/403`: Invalid credentials.

---

### Admin API: Get Users
- **Endpoint**: `/admin/api/users`
- **Method**: `POST`
- **Description**: Retrieves all users.
- **Request Body**:
  - `admin_key_1`: Encrypted admin key part 1.
  - `admin_key_2`: Encrypted admin key part 2.
  - `salt`: Encryption salt.
- **Responses**:
  - `200 OK`: List of users.
  - `400/401/403/500`: Various errors.

---

### Admin API: Get Academic Bot
- **Endpoint**: `/admin/api/personas`
- **Method**: `POST`
- **Description**: Retrieves all personas.
- **Request Body**:
  - `admin_key_1`: Encrypted admin key part 1.
  - `admin_key_2`: Encrypted admin key part 2.
  - `salt`: Encryption salt.
- **Responses**:
  - `200 OK`: List of personas.
  - `400/401/403/500`: Various errors.

---

### Admin API: Get Files
- **Endpoint**: `/admin/api/files`
- **Method**: `POST`
- **Description**: Retrieves all files.
- **Request Body**:
  - `admin_key_1`: Encrypted admin key part 1.
  - `admin_key_2`: Encrypted admin key part 2.
  - `salt`: Encryption salt.
- **Responses**:
  - `200 OK`: List of files.
  - `400/401/403/500`: Various errors.

---

### Email Chat
- **Endpoint**: `/api/email_chat`
- **Method**: `POST`
- **Description**: Emails the chat transcript to the user.
- **Request Body**:
  - `personaName`: Name of the persona.
  - `personaDescription`: Description of the persona.
  - `conversation`: Conversation history.
- **Responses**:
  - `200 OK`: Email sent.
  - `400/404/500`: Various errors.

---

### Email Chat with Email
- **Endpoint**: `/api/email_chat_with_email`
- **Method**: `POST`
- **Description**: Emails the chat transcript to a specified email.
- **Request Body**:
  - `userEmail`: Recipient's email address.
  - `personaName`: Name of the persona.
  - `personaDescription`: Description of the persona.
  - `conversation`: Conversation history.
- **Responses**:
  - `200 OK`: Email sent.
  - `400/500`: Various errors.

---

### Usage History
- **Endpoint**: `/usage_history`
- **Method**: `GET, POST`
- **Description**: Displays the user's usage history.
- **Responses**:
  - `200 OK`: Usage history rendered.
  - `404 Not Found`: User not logged in.

### Usage History API
- **Endpoint**: `/usage_history/api/`
- **Method**: `POST`
- **Description**: Retrieves the authenticated user's usage history across various models and features.
- **Responses**:
  - `200 OK`: Usage history data.
  - `401 Unauthorized`: User not authenticated.
  - `500 Internal Server Error`: Error querying data.

---

### Admin Access API
- **Endpoint**: `/admin_access/api/`
- **Method**: `POST`
- **Description**: Provides admin access to all data models and aggregates token usage per user.
- **Request Body**:
  - `admin_key_1`: Encrypted admin key part 1.
  - `admin_key_2`: Encrypted admin key part 2.
  - `salt`: Encryption salt.
- **Responses**:
  - `200 OK`: Aggregated data.
  - `400/401/403/500`: Various errors during validation or query execution.

---

### Update Global Variable Email Domain
- **Endpoint**: `/admin/global_variable_email_domain`
- **Method**: `GET, POST`
- **Description**: Fetches or updates the global variable for email domain validation.
- **Request Body** (POST):
  - `email_domain`: New email domain.
  - `admin_key_1`, `admin_key_2`, `salt`: Encrypted admin credentials.
- **Responses**:
  - `200 OK`: Email domain updated or retrieved.
  - `400/403/500`: Various errors.

---

### Update Global Variable API Keys
- **Endpoint**: `/admin/global_variable_api_keys`
- **Method**: `GET, POST`
- **Description**: Retrieves or updates global API keys for OpenAI and Google Custom Search.
- **Request Body** (POST):
  - `open_ai_key`, `google_search_api_key`: New API keys.
  - `admin_key_1`, `admin_key_2`, `salt`: Encrypted admin credentials.
- **Responses**:
  - `200 OK`: API keys updated or retrieved.
  - `400/403/500`: Various errors.

---

### Update Auto Access Admin Keys
- **Endpoint**: `/admin/global_variable_auto_access_admin_keys`
- **Method**: `POST`
- **Description**: Toggles automatic admin key access for users.
- **Request Body**:
  - `auto_admin_keys_access`: Boolean flag.
- **Responses**:
  - `200 OK`: Auto-access updated successfully.
  - `500 Internal Server Error`: Error during update.

---

### Get Auto Access Admin Keys Status
- **Endpoint**: `/admin/get_auto_access_admin_keys_status`
- **Method**: `GET`
- **Description**: Retrieves the current status of automatic admin key access.
- **Responses**:
  - `200 OK`: Current auto-access status.
  - `500 Internal Server Error`: Error querying status.

---

### Upload Admin Logo
- **Endpoint**: `/admin/global_variable_logo_image`
- **Method**: `POST`
- **Description**: Uploads a logo image for admin use.
- **Request Body**:
  - `image`: Image file.
- **Responses**:
  - `200 OK`: Logo uploaded successfully.
  - `400/500`: Errors related to file upload.

---

### Admin Handle User Data
- **Endpoint**: `/admin/send-user-data`
- **Method**: `POST`
- **Description**: Grants or revokes admin key access for a user.
- **Request Body**:
  - `user_id`: ID of the user to update.
- **Responses**:
  - `200 OK`: User data updated successfully.
  - `400/500`: Errors during update.

---
