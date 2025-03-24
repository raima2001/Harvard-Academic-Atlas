# import os
# import pytest
# import sys
# from unittest.mock import patch,  MagicMock
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# from api_service.py_files.retrieval import ( 
#     get_google_organic_results,
#     scrape_website,
#     combined_scrape_function,
#     saveFileOpenAI,
#     startBotCreation,
#     delete_assistant,
#     delete_assistant_and_file,
#     startThreadCreation,
#     runAssistant,
#     process_url,
#     sanitize_filename,
#     compress_audio,
#     compressed_audio_to_text_file
# )

# @pytest.fixture
# def dummy_audio_file(tmp_path):
#     """Fixture to create a dummy audio file."""
#     dummy_file = tmp_path / "test_audio.mp3"
#     dummy_file.write_bytes(b"dummy audio content")
#     return dummy_file


# def dummy_text_file(tmp_path):
#     """Fixture to create a dummy text file."""
#     dummy_file = tmp_path / "test_text.txt"
#     dummy_file.write_text("Dummy content")
#     return dummy_file

# def dummy_openai_client():
#     """Fixture for mocking the OpenAI client."""
#     with patch("retrieval.OpenAI") as mock_openai:
#         mock_client = MagicMock()
#         mock_openai.return_value = mock_client
#         yield mock_client


# @patch("retrieval.googleapiclient.discovery.build")
# def test_get_google_organic_results(mock_build):
#     """Test fetching Google organic results."""
#     mock_service = MagicMock()
#     mock_build.return_value = mock_service
#     mock_response = {"items": [{"link": "https://example.com"}]}
#     mock_service.cse().list().execute.return_value = mock_response

#     results = get_google_organic_results("test query", "fake_key", "fake_cse_id")
#     assert results == ["https://example.com"]


# @patch("retrieval.requests.get")
# def test_scrape_website(mock_get):
#     """Test scraping a website."""
#     mock_response = MagicMock()
#     mock_response.text = "<html><body>Test content</body></html>"
#     mock_get.return_value = mock_response

#     result = scrape_website("https://example.com")
#     assert "Test content" in result


# @patch("retrieval.scrape_website", return_value="Scraped Content")
# @patch("retrieval.get_google_organic_results", return_value=["https://example1.com", "https://example2.com"])
# @patch("retrieval.OpenAI")
# def test_combined_scrape_function(mock_openai, mock_get_results, mock_scrape):
#     """Test the combined scrape function."""
#     mock_client = MagicMock()
#     mock_openai.return_value = mock_client
#     mock_client.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content="Test response"))])

#     response, urls = combined_scrape_function("query", "api_key", "developer_key")
#     assert response == "Test response"
#     assert urls == ["https://example1.com", "https://example2.com"]


# @patch("builtins.open", new_callable=MagicMock)
# def test_saveFileOpenAI(mock_open, dummy_openai_client, dummy_text_file):
#     """Test saving a file to OpenAI."""
#     dummy_openai_client.files.create.return_value = MagicMock(id="file_id")

#     result = saveFileOpenAI(str(dummy_text_file), "api_key")
#     assert result == "file_id"


# @patch("retrieval.OpenAI")
# def test_startBotCreation(mock_openai):
#     """Test bot creation."""
#     mock_client = MagicMock()
#     mock_openai.return_value = mock_client
#     mock_client.beta.assistants.create.return_value = MagicMock(id="bot_id")

#     result = startBotCreation(["file_id"], "api_key", "title", "prompt")
#     assert result == "bot_id"


# @patch("retrieval.OpenAI")
# def test_delete_assistant(mock_openai):
#     """Test deleting an assistant."""
#     mock_client = MagicMock()
#     mock_openai.return_value = mock_client
#     mock_client.beta.assistants.delete.return_value = MagicMock(deleted=True)

#     result = delete_assistant("assistant_id", "api_key")
#     assert result == "Assistant deleted successfully."


# @patch("retrieval.OpenAI")
# def test_delete_assistant_and_file(mock_openai):
#     """Test deleting an assistant and its associated file."""
#     mock_client = MagicMock()
#     mock_openai.return_value = mock_client
#     mock_client.beta.assistants.files.delete.return_value = MagicMock()
#     mock_client.beta.assistants.delete.return_value = MagicMock()

#     result = delete_assistant_and_file("assistant_id", "file_id", "api_key")
#     assert result


# @patch("retrieval.OpenAI")
# def test_startThreadCreation(mock_openai):
#     """Test thread creation."""
#     mock_client = MagicMock()
#     mock_openai.return_value = mock_client
#     mock_client.beta.threads.create.return_value = MagicMock(id="thread_id", object="thread")

#     result = startThreadCreation([{"role": "user", "content": "test"}], "api_key")
#     assert result == "thread_id"


# @patch("retrieval.OpenAI")
# def test_runAssistant(mock_openai):
#     """Test running an assistant."""
#     mock_client = MagicMock()
#     mock_openai.return_value = mock_client
#     mock_client.beta.threads.runs.create.return_value = MagicMock(id="run_id")
#     mock_client.beta.threads.runs.retrieve.return_value = MagicMock(status="completed")
#     mock_client.beta.threads.messages.list.return_value = MagicMock(data=[MagicMock(content=[MagicMock(text=MagicMock(value="Test Message"))])])

#     message, reference = runAssistant("thread_id", "assistant_id", "api_key", "serp_api_key")
#     assert message == "Test Message"
#     assert reference is None


# @patch("retrieval.requests.get")
# @patch("retrieval.YouTubeTranscriptApi.get_transcript")
# def test_process_url_youtube(mock_get_transcript, mock_get):
#     """Test processing a YouTube URL."""
#     mock_get_transcript.return_value = [{"text": "test transcript"}]
#     result, content = process_url("https://youtube.com/watch?v=test")
#     assert result
#     assert content == "test transcript"


# @patch("retrieval.os.path.getsize", return_value=50 * 1024 * 1024)
# @patch("retrieval.AudioSegment.from_file")
# def test_compress_audio(mock_audio, mock_getsize, dummy_audio_file, tmp_path):
#     """Test compressing audio."""
#     mock_audio.return_value = MagicMock()

#     compressed_path, compressed_size = compress_audio(str(dummy_audio_file), str(tmp_path))
#     assert compressed_path.endswith("_compressed_64k.mp3")
#     assert compressed_size <= 24 * 1024 * 1024  # 24 MB


# @patch("retrieval.openai.OpenAI")
# def test_compressed_audio_to_text_file(mock_openai, dummy_audio_file, tmp_path):
#     """Test converting compressed audio to text file."""
#     mock_client = MagicMock()
#     mock_openai.return_value = mock_client
#     mock_client.audio.transcriptions.create.return_value = "Test Transcript"

#     result = compressed_audio_to_text_file(str(dummy_audio_file), str(tmp_path), "api_key")
#     assert result.endswith("_transcript.txt")
