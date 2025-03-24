import os
import sys
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from unittest.mock import patch
from api_service.py_files.emails import (  
    convert_and_delete_conversation_to_docx,
    clean_text,
    create_word_doc,
    send_email_with_attachment,
    send_welcome_email,
    send_audio_email_with_attachment,
    send_invitation_email
)

@pytest.fixture
def mock_smtp():
    with patch("smtplib.SMTP_SSL") as mock_smtp_class:
        yield mock_smtp_class.return_value

def test_convert_and_delete_conversation_to_docx(tmp_path):
    """Test converting and deleting markdown files to DOCX."""
    heading = "Test Heading"
    description = "Test Description"
    conversation = [{"role": "user", "content": "Hello!"}]
    filename = tmp_path / "output.docx"

    with patch("pypandoc.convert_file", return_value=True), patch("os.remove") as mock_remove:
        md_path = convert_and_delete_conversation_to_docx(heading, description, conversation, str(filename))
        assert md_path.endswith(".md")
        mock_remove.assert_not_called()  # Ensure deletion is in a thread

def test_clean_text():
    """Test cleaning text from markdown symbols."""
    input_text = "**Bold** ##Heading###"
    expected_output = "Bold Heading"
    assert clean_text(input_text) == expected_output

def test_create_word_doc(tmp_path):
    """Test creating a Word document."""
    heading = "Test Heading"
    description = "Test Description"
    conversation = [{"role": "user", "content": "Hello!"}]
    filename = tmp_path / "output.docx"

    assert create_word_doc(heading, description, conversation, str(filename))
    assert os.path.exists(filename)

@patch("smtplib.SMTP_SSL")
def test_send_email_with_attachment(mock_smtp, tmp_path):
    """Test sending an email with an attachment."""
    filename = tmp_path / "test.txt"
    filename.write_text("Test content")
    result = send_email_with_attachment("test@example.com", "Test Subject", str(filename))
    assert result is True
    mock_smtp.assert_called_once()

@patch("smtplib.SMTP_SSL")
def test_send_welcome_email(mock_smtp):
    """Test sending a welcome email."""
    result = send_welcome_email("test@example.com", "12345", "password")
    assert result == "Email sent successfully!"
    mock_smtp.assert_called_once()

@patch("smtplib.SMTP_SSL")
def test_send_audio_email_with_attachment(mock_smtp, tmp_path):
    """Test sending an audio email with an attachment."""
    filename = tmp_path / "audio.mp3"
    filename.write_text("Audio content")
    result = send_audio_email_with_attachment("test@example.com", "Test Subject", str(filename))
    assert result is True
    mock_smtp.assert_called_once()

@patch("smtplib.SMTP_SSL")
def test_send_invitation_email(mock_smtp):
    """Test sending an invitation email."""
    result = send_invitation_email(
        "invitee@example.com",
        "Test Subject",
        "http://example.com/chat",
        "http://example.com/form",
        "TestUser",
        "TestRun"
    )
    assert "Invitation email sent successfully" in result
    mock_smtp.assert_called_once()