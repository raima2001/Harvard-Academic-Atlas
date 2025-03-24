
import os
import subprocess
from unittest.mock import patch, call
import pytest
import sys

# Add workflow_manager.py to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../workflow')))
from workflow_manager import WorkflowManager


@pytest.fixture
def manager():
    """Fixture to create a WorkflowManager instance."""
    return WorkflowManager()


def test_load_env(manager, tmp_path):
    """Test loading environment variables from .env file."""
    # Create a temporary .env file
    env_file = tmp_path / ".env"
    env_file.write_text("TEST_KEY=VALUE\nANOTHER_KEY=123")

    manager.env_file = str(env_file)
    manager.load_env()

    assert os.getenv("TEST_KEY") == "VALUE"
    assert os.getenv("ANOTHER_KEY") == "123"


@patch("os.path.exists", return_value=False)
@patch("logging.warning")
def test_load_env_no_env_file(mock_logging_warning, mock_path_exists, manager):
    """Test load_env logs a warning if .env file is missing."""
    manager.load_env()
    mock_logging_warning.assert_called_once_with(".env not found. Ensure environment variables are set.")


@patch("subprocess.run")
def test_run_docker_service(mock_subprocess_run, manager):
    """Test running a specific Docker service."""
    mock_subprocess_run.return_value = None  # Simulate successful run

    manager.run_docker_service("data_extraction")

    mock_subprocess_run.assert_called_once_with(
        ["docker-compose", "up", "--build", "--no-deps", "--abort-on-container-exit", "data_extraction"],
        check=True,
    )


@patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "docker-compose"))
@patch("logging.error")
def test_run_docker_service_error(mock_logging_error, mock_subprocess_run, manager):
    """Test run_docker_service logs an error if subprocess.run fails."""
    service_name = "data_extraction"
    with pytest.raises(subprocess.CalledProcessError):
        manager.run_docker_service(service_name)
    mock_logging_error.assert_called_once_with(
        f"Service {service_name} failed with error: Command 'docker-compose' returned non-zero exit status 1."
    )


@patch("subprocess.run")
def test_run_workflow(mock_subprocess_run, manager):
    """Test running the entire workflow."""
    mock_subprocess_run.return_value = None  # Simulate successful service runs

    manager.run_workflow()

    # Verify all stages were called in sequence
    expected_calls = [
        call(
            ["docker-compose", "up", "--build", "--no-deps", "--abort-on-container-exit", stage["docker_service"]],
            check=True,
        )
        for stage in manager.STAGES.values()
    ]
    mock_subprocess_run.assert_has_calls(expected_calls)


@patch("subprocess.run")
def test_start_api_service(mock_subprocess_run, manager):
    """Test starting the API service only."""
    mock_subprocess_run.return_value = None  # Simulate successful run

    manager.start_api_service()

    mock_subprocess_run.assert_called_once_with(
        ["docker-compose", "up", "--build", "--no-deps", "--abort-on-container-exit", "api_service"],
        check=True,
    )

# @patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "docker-compose"))
# @patch("logging.error")
# def test_run_workflow_error_handling(mock_logging_error, mock_subprocess_run, manager):
#     """Test that run_workflow stops on error and logs it."""
#     manager.STAGES = {
#         "test_stage": {
#             "description": "Test stage",
#             "docker_service": "data_extraction",
#         }
#     }

#     with pytest.raises(subprocess.CalledProcessError):
#         manager.run_workflow()

#     # Verify error logging
#     mock_logging_error.assert_called_once_with(
#         "Service data_extraction failed with error: Command 'docker-compose' returned non-zero exit status 1."
#     )

# @patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "docker-compose"))
# @patch("builtins.print")
# def test_start_api_service_error(mock_print, mock_subprocess_run, manager):
#     """Test that start_api_service logs an error if the service fails."""
#     manager.start_api_service()

#     # Verify the error message was printed
#     mock_print.assert_any_call(
#         "Error starting the API service: Command 'docker-compose' returned non-zero exit status 1. Check logs for details."
#     )


# @patch("builtins.input", side_effect=["1", "3"])
# @patch("workflow_manager.WorkflowManager.run_workflow")
# @patch("workflow_manager.WorkflowManager.start_api_service")
# def test_main_menu(mock_start_api_service, mock_run_workflow, mock_input):
#     """Test the main menu logic."""
#     manager = WorkflowManager()

#     with patch("builtins.print") as mock_print:
#         with pytest.raises(SystemExit):
#             manager.load_env = lambda: None  # Mock load_env to avoid dependency on .env
#             manager.run_workflow = mock_run_workflow
#             manager.start_api_service = mock_start_api_service

#             # Simulate the main menu loop
#             exec("WorkflowManager.__name__ == '__main__'")

#     # Verify run_workflow was called once
#     mock_run_workflow.assert_called_once()
#     # Verify start_api_service was not called
#     mock_start_api_service.assert_not_called()
#     # Ensure correct messages were printed
#     mock_print.assert_any_call("\nWorkflow Manager Menu:")
#     mock_print.assert_any_call("1. Run Full Workflow")
#     mock_print.assert_any_call("3. Exit")