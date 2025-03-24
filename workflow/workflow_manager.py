import subprocess
import os
import logging

# Configure logging
logging.basicConfig(
    filename="workflow_manager.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Define workflow stages


# Workflow Manager
class WorkflowManager:
    STAGES = {
        "data_extraction": {
            "description": "Extracting data from Harvard Law School website",
            "docker_service": "data_extraction",
        },
        "data_cleaning": {
            "description": "Cleaning and processing the extracted data",
            "docker_service": "cleaning_data",
        },
        "vectorization": {
            "description": "Vectorizing cleaned data and storing embeddings",
            "docker_service": "vectorizer",
        },
        "dvc_push": {
            "description": "Tracking and pushing data with DVC",
            "docker_service": "dvc",
        },
        "api_service": {
            "description": "Starting the Flask API and frontend service",
            "docker_service": "api_service",
        },
    }

    def __init__(self, env_file=".env"):
        self.env_file = env_file


    def load_env(self):
        """Load environment variables from .env file."""
        if os.path.exists(self.env_file):
            logging.info(f"Loading environment variables from {self.env_file}")
            with open(self.env_file) as f:
                for line in f:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        os.environ[key] = value
        else:
            logging.warning(f"{self.env_file} not found. Ensure environment variables are set.") #53

    def run_docker_service(self, service_name):
        """Run a specific Docker service using docker-compose."""
        try:
            logging.info(f"Starting service: {service_name}")
            subprocess.run(
                ["docker-compose", "up", "--build", "--no-deps", "--abort-on-container-exit", service_name],
                check=True,
            )
            logging.info(f"Service {service_name} completed successfully.")
        except subprocess.CalledProcessError as e: #64
            logging.error(f"Service {service_name} failed with error: {e}")
            raise #66

    def run_workflow(self):
        """Execute the entire workflow in sequence."""
        for stage, details in self.STAGES.items():
            print(f"\nStarting: {details['description']}")
            try:
                self.run_docker_service(details["docker_service"])
            except Exception as e: #75
                print(f"Error in stage {stage}: {e}. Check logs for more details.")
                break #77
            print(f"Completed: {details['description']}")

        print("\nWorkflow completed. Check workflow_manager.log for details.")

    def start_api_service(self):
        """Start the API service only."""
        print("\nStarting the API service...")
        try:
            self.run_docker_service("api_service")
        except Exception as e: #87
            print(f"Error starting the API service: {e}. Check logs for details.") #88


if __name__ == "__main__":
    manager = WorkflowManager() #92
    manager.load_env()

    # Main menu for managing the workflow
    while True:
        print("\nWorkflow Manager Menu:")
        print("1. Run Full Workflow")
        print("2. Start API Service Only")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            manager.run_workflow()
        elif choice == "2":
            manager.start_api_service()
        elif choice == "3":
            print("Exiting Workflow Manager.")
            break
        else:
            print("Invalid choice. Please try again.") #111
