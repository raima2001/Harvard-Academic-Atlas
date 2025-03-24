import json, os, threading, hashlib, base64, openai, re, logging, time, requests, logging
from cryptography.fernet import Fernet
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError
from datetime import datetime
import googleapiclient.discovery
import tiktoken

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

ALLOWED_EXTENSIONS_KNOWLEDGE = {'docx', 'html', 'json', 'md', 'pdf', 'pptx', 'txt', 'mp3', 'mp4'}
UPLOAD_FOLDER_KNOWLEDGE = 'knowledge_base'


def is_openai_key_valid(api_key):
    url = "https://api.openai.com/v1/engines"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.get(url, headers=headers)

    return response.status_code == 200

'''
def is_serp_key_valid(serp_api_key):
    # URL for a simple SerpApi request, like a search with minimal parameters
    url = "https://serpapi.com/search.json"
    params = {
        "q": "test",  # a simple query
        "api_key": serp_api_key,
        "engine": "google"  # specifying the search engine
    }

    try:
        response = requests.get(url, params=params)
        return response.status_code == 200

    except requests.exceptions.RequestException as e:
        # Handle any exceptions that may occur and print the error
        print("API Request Error:", e)
        return False'''

#Now using Google Custom API instead of SERP API
def is_serp_key_valid(developerKey):
    INPUT_CSE_ID = "e4b6b224faa9941d0"
    try:
        # Initialize the Google API client
        service = googleapiclient.discovery.build("customsearch", "v1", developerKey=developerKey)

        # Make a test search request
        res = service.cse().list(q="test", cx=INPUT_CSE_ID, num=1).execute()

        # Check if the response contains search results
        if 'items' in res:
            return True
        else:
            return False
    except googleapiclient.errors.HttpError as e:
        # Handle any exceptions and return False
        print("API Request Error:", e)
        return False


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_file_knowledge(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_KNOWLEDGE


def encrypt_api_key(api_key, key):
    try:
        fernet = Fernet(key)
        return fernet.encrypt(api_key.encode())
    except Exception as e:
        # Handle encryption error
        raise Exception(f"Encryption error: {e}")


def decrypt_api_key(encrypted_key, key, is_int=False):
    try:
        fernet = Fernet(key)
        decrypted_key = fernet.decrypt(encrypted_key).decode()
        return int(decrypted_key) if is_int else decrypted_key
    except Exception as e:
        # Handle decryption error
        raise Exception(f"Decryption error: {e}")


def is_password_valid(password: str) -> bool:
    # Check if password length is at least 8 characters
    if len(password) < 8:
        return False

    # Check if password contains at least one digit and one special character
    if not re.search(r'\d', password) or not re.search(r'[@$!%*#?&]', password):
        return False

    return True


def delayed_file_deletion(file_path: str, delay_in_seconds: int = 30) -> None:
    time.sleep(delay_in_seconds)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"File {file_path} deleted successfully after delay.")
            print(f"File {file_path} deleted successfully after delay.")
    except OSError as e:
        logging.error(f"Error while deleting file {file_path}: {e}")
        print(f"Error while deleting file {file_path}: {e}")


def delayed_file_deletion_for_evaluation(file_path: str, delay_in_seconds: int = 20, retry_attempts: int = 3, retry_interval: int = 5):
    time.sleep(delay_in_seconds)
    attempts = 0
    while attempts < retry_attempts:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"File {file_path} deleted successfully after delay.")
                break  # Exit the loop if file is successfully deleted
            else:
                print(f"File {file_path} does not exist. No need for further deletion attempts.")
                break  # Exit the loop if file does not exist
        except OSError as e:
            attempts += 1
            print(f"Attempt {attempts} - Error while deleting file {file_path}: {e}")
            if e.errno == 2:  # Error code for "File not found"
                break  # Exit the loop if file is not found
            time.sleep(retry_interval)


def encrypt_and_encode_api_key(api_key):
    # Generate a random salt (key)
    salt = Fernet.generate_key()

    # Encrypt the API key using the salt
    fernet = Fernet(salt)
    encrypted_api_key = fernet.encrypt(api_key.encode())

    # Encode the salt and encrypted API key
    encoded_salt = base64.urlsafe_b64encode(salt).decode('utf-8')
    encoded_api_key = base64.urlsafe_b64encode(encrypted_api_key).decode('utf-8')

    return encoded_api_key, encoded_salt

def decrypt_and_decode_api_key(encoded_api_key, salt):
    print(f"Encoded API Key: {encoded_api_key}")
    print(f"Encoded Salt: {salt}")

    # Validate the salt
    try:
        decoded_salt = base64.urlsafe_b64decode(salt)
        print(f"Decoded Salt Length: {len(decoded_salt)}")
        if len(decoded_salt) != 32:
            raise ValueError("Salt must decode to exactly 32 bytes.")
    except Exception as e:
        raise ValueError(f"Invalid salt provided: {e}")

    # Decode the API key
    decoded_api_key = base64.urlsafe_b64decode(encoded_api_key)

    # Decrypt the API key
    fernet = Fernet(decoded_salt)
    return fernet.decrypt(decoded_api_key).decode('utf-8')

def save_and_resize_image(image):
    try:
        max_size = 500 * 1024  # 500 KB
        filename = secure_filename(image.filename)
        timestamped_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
        image_path = os.path.join(UPLOAD_FOLDER, timestamped_filename)
        image.save(image_path)
        
        # Resize image if it's larger than 500 KB
        if os.path.getsize(image_path) > max_size:
            resize_image(image_path, max_size)

        return image_path
    except IOError as e:
        logging.error(f"Error saving image: {e}")
        raise  # You can decide to handle it differently or re-raise the error

def resize_image(image_path, max_size, attempt=1):
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            img = img.resize((int(width * 0.8), int(height * 0.8)), Image.ANTIALIAS)
            img.save(image_path, quality=85)

            # Check the file size and resize again if necessary
            if os.path.getsize(image_path) > max_size and attempt < 10:
                resize_image(image_path, max_size, attempt + 1)
    except (IOError, UnidentifiedImageError) as e:
        logging.error(f"Error resizing image: {e}")
        raise  # Decide how you want to handle this error, either re-raise or something else
    except RecursionError as e:
        logging.error(f"Recursive error in resizing image: {e}")
        raise  # This might indicate an issue with the resizing logic


def calculate_token_count(input_data, output_string_1):

    # Convert input_data to a string if it's a list
    if isinstance(input_data, list):
        input_string = ' '.join(item['content'] for item in input_data)
    else:
        input_string = input_data

    # Convert output_string_1 to a string if it's a list
    if isinstance(output_string_1, list):
        output_string_1 = ' '.join(item['content'] for item in output_string_1)

    # Get encoding
    encoding = tiktoken.get_encoding('cl100k_base')
    
    # Calculate token counts
    num_tokens_input = len(encoding.encode(input_string))
    num_tokens_output = len(encoding.encode(output_string_1)) 

    return num_tokens_input, num_tokens_output
