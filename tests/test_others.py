import os
import pytest
import sys
from unittest.mock import patch,  MagicMock
from PIL import Image
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from cryptography.fernet import Fernet
from api_service.py_files.others import (  # Replace `your_module_name` with your actual module name
    is_openai_key_valid,
    is_serp_key_valid,
    allowed_file,
    allowed_file_knowledge,
    encrypt_api_key,
    decrypt_api_key,
    is_password_valid,
    delayed_file_deletion,
    encrypt_and_encode_api_key,
    save_and_resize_image,
    resize_image,
    calculate_token_count,
)

@pytest.fixture
def dummy_image(tmp_path):
    """Fixture to create a dummy image for testing."""
    image_path = tmp_path / "test_image.jpg"
    with open(image_path, "wb") as f:
        f.write(b"dummy image content")
    return image_path

def test_is_openai_key_valid():
    """Test OpenAI key validation."""
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        assert is_openai_key_valid("dummy_key") is True
        mock_get.return_value.status_code = 401
        assert is_openai_key_valid("dummy_key") is False

def test_is_serp_key_valid():
    """Test SERP API key validation."""
    with patch("googleapiclient.discovery.build") as mock_build:
        mock_build.return_value.cse.return_value.list.return_value.execute.return_value = {"items": [{}]}
        assert is_serp_key_valid("dummy_key") is True

        mock_build.return_value.cse.return_value.list.return_value.execute.return_value = {}
        assert is_serp_key_valid("dummy_key") is False

def test_allowed_file():
    """Test allowed file extensions."""
    assert allowed_file("test.jpg") is True
    assert allowed_file("test.txt") is False

def test_allowed_file_knowledge():
    """Test allowed knowledge file extensions."""
    assert allowed_file_knowledge("test.pdf") is True
    assert allowed_file_knowledge("test.exe") is False

def test_encrypt_api_key():
    """Test encrypting API keys."""
    key = Fernet.generate_key()
    encrypted = encrypt_api_key("dummy_key", key)
    assert isinstance(encrypted, bytes)

def test_decrypt_api_key():
    """Test decrypting API keys."""
    key = Fernet.generate_key()
    encrypted = encrypt_api_key("dummy_key", key)
    decrypted = decrypt_api_key(encrypted, key)
    assert decrypted == "dummy_key"

def test_is_password_valid():
    """Test password validity."""
    assert is_password_valid("Password123!") is True
    assert is_password_valid("short") is False
    assert is_password_valid("nopunctuations123") is False

@patch("os.path.exists", return_value=True)
@patch("os.remove")
def test_delayed_file_deletion(mock_remove, mock_exists):
    """Test delayed file deletion."""
    delayed_file_deletion("dummy_path", delay_in_seconds=0)
    mock_remove.assert_called_once_with("dummy_path")

def test_encrypt_and_encode_api_key():
    """Test encrypting and encoding API keys."""
    api_key = "dummy_key"
    encoded_api_key, encoded_salt = encrypt_and_encode_api_key(api_key)
    assert isinstance(encoded_api_key, str)
    assert isinstance(encoded_salt, str)

# def test_decrypt_and_decode_api_key():
#     """Test decrypting and decoding API keys."""
#     api_key = "dummy_key"
#     encoded_api_key, encoded_salt = encrypt_and_encode_api_key(api_key)
#     decrypted_api_key = decrypt_and_decode_api_key(encoded_api_key, encoded_salt)
#     assert decrypted_api_key == api_key

# @patch("os.path.getsize", return_value=600 * 1024)  # Mock file size larger than 500 KB
# @patch("PIL.Image.open")
# def test_save_and_resize_image(mock_image_open, mock_getsize, tmp_path):
#     """Test saving and resizing an image."""
#     # Create a dummy image file
#     dummy_image_file = tmp_path / "test_image.jpg"
#     dummy_image_file.write_bytes(b"dummy image content")

#     # Mock the image object
#     mock_image = MagicMock()
#     mock_image_open.return_value = mock_image

#     # Call the function
#     with patch("your_module.secure_filename", return_value="test_image.jpg"):
#         result = save_and_resize_image(dummy_image_file)

#     # Assert that the function returns the correct path
#     assert result.endswith("test_image.jpg")
#     # Verify that PIL.Image.open was called
#     mock_image_open.assert_called_once_with(dummy_image_file)
#     # Check if the save method was called
#     mock_image.save.assert_called()


# @patch("os.path.getsize", side_effect=[600 * 1024, 400 * 1024])  # Simulate size reduction
# @patch("PIL.Image.open")
# def test_resize_image(mock_image_open, mock_getsize, tmp_path):
#     """Test resizing an image."""
#     # Create a dummy image file
#     dummy_image_file = tmp_path / "test_image.jpg"
#     dummy_image_file.write_bytes(b"dummy image content")

#     # Mock the image object
#     mock_image = MagicMock()
#     mock_image.size = (800, 600)  # Original size
#     mock_image_open.return_value = mock_image

#     resize_image(dummy_image_file, max_size=500 * 1024)

#     # Verify that PIL.Image.open was called
#     mock_image_open.assert_called_once_with(dummy_image_file)
#     # Check if the resize method was called
#     mock_image.resize.assert_called()
#     # Check if the save method was called
#     mock_image.save.assert_called()

def test_calculate_token_count():
    """Test token count calculation."""
    input_data = [{"content": "Hello world!"}]
    output_string = "This is a response."
    with patch("tiktoken.get_encoding") as mock_encoding:
        mock_encoding.return_value.encode.side_effect = lambda x: list(x)
        num_tokens_input, num_tokens_output = calculate_token_count(input_data, output_string)
        assert num_tokens_input == len("Hello world!")
        assert num_tokens_output == len("This is a response.")
