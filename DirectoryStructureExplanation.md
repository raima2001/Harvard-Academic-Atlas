### Updated Explanation of the Directory Structure - MS5

The following directory structure reflects the latest updates to the **`ac215_masalachai`** project, including all components, their roles, and new additions for Milestone 5.

---

### **`ac215_masalachai/`**: Root Directory
The root directory contains all the files and subdirectories necessary for the project pipeline, frontend, backend, orchestration logic, Kubernetes deployment, and Ansible automation.

#### **`data/`**
This shared directory is tracked by **DVC** (Data Version Control) and mounted into Docker containers to facilitate data sharing between pipeline stages.

- **`courses_data_all_pages.csv`**: The raw data extracted from the Harvard Law School website.
- **`HLS_cleaned_data.csv`**: Cleaned and processed data in CSV format.
- **`HLS_cleaned_data.pdf`**: Cleaned data exported in PDF format.
- **`HLS_cleaned_data.docx`**: Cleaned data exported in DOCX format.
- **`logs/`**: Stores logs of interactions with the Large Language Model (LLM).
  - **`llm_interactions.log`**: Tracks LLM prompts and responses for debugging and review.

---

#### **`vault/`**
Contains milestone-specific images and screenshots used for reporting and documentation (e.g., for Milestone 5).

---

#### **`src/`**
This directory contains all source code, Docker configurations, and orchestration files.

##### **`docker-compose.yml`**
The Docker Compose file orchestrates the execution of all containers in the pipeline, ensuring proper sequencing and volume sharing.

##### **`.env`**
Environment variables file that stores sensitive configurations like API keys. Examples:
```plaintext
OPENAI_API_KEY=<your_openai_api_key>
PINECONE_API_KEY=<your_pinecone_api_key>
PINECONE_ENVIRONMENT=<your_pinecone_environment>
```

---

### **`datapipeline/`**
Manages the data processing pipeline.

#### **`data_extraction/`**
- **`Dockerfile`**: Dockerfile to create an isolated environment for data extraction.
- **`Pipfile`**: Manages Python dependencies for this stage (e.g., `selenium`, `beautifulsoup4`).
- **`data_extraction.py`**: Script that scrapes course data from the Harvard Law School website and saves it as a CSV file.

#### **`cleaning_data/`**
- **`Dockerfile`**: Dockerfile to create an isolated environment for data cleaning.
- **`Pipfile`**: Manages Python dependencies for this stage (e.g., `pandas`, `fpdf`, `python-docx`).
- **`cleaning_data.py`**: Script that processes raw data, handles missing values, and exports cleaned data to multiple formats (CSV, PDF, DOCX).

---

### **`vectorizer/`**
Handles data vectorization and embedding generation.

- **`Dockerfile`**: Defines the environment for vectorizing cleaned data.
- **`Pipfile`**: Manages Python dependencies (e.g., `pinecone-client`, `openai`).
- **`pdf_docx_to_vector.py`**: Script that:
  - Converts DOCX and PDF files into vector embeddings.
  - Interacts with Pinecone and OpenAI for vector storage and querying.
- **`db/`**: Contains the embeddings database for local storage and backup.
  - **`chroma.sqlite3`**: A local snapshot of vector embeddings for faster querying.

---

### **`dvc/`**
Manages data versioning and tracking.

- **`Dockerfile`**: Configures the DVC container.
- **`.dvc/`**: DVC configuration directory for remote storage settings.
  - **`config`**: Specifies remote storage paths (e.g., S3, GCP).
- **`data.dvc`**: Tracks the `data/` directory, enabling reproducibility and remote syncing.

---

### **`api-service/`**
Houses the Flask API backend and frontend integration.

- **`Dockerfile`**: Defines the environment for the Flask API.
- **`Pipfile`**: Manages Python dependencies for the API service (e.g., `Flask`, `Flask-SQLAlchemy`).
- **`Pipfile.lock`**: Ensures consistent dependency versions.
- **`main.py`**: Flask application:
  - Serves the frontend.
  - Provides RESTful APIs for querying processed data.
  - Integrates with SQLite for database management.
- **`requirements.txt`**: Contains Python dependencies in `pip` format.
- **`instance/`**:
  - **`site.db`**: SQLite database for application data (e.g., user logs, preferences).
- **`templates/`**:
  - **`index.html`**: Home page of the frontend.
  - **Additional HTML Files**: Pages for dashboards, user profiles, etc.
- **`static/`**:
  - **`images/`**: Contains images used by the frontend.
- **`py_files/`**:
  - Backend helper scripts (e.g., `utils.py`, `database_helper.py`).
- **`knowledgebase/`**:
  - Stores resources for students (e.g., `knowledge.json`).
- **`chat_emails/`**:
  - Logs email-based interactions and notifications.

---

### **`kubernetes/`**
Contains configuration files for deploying the application on Kubernetes.

- **`api-deployment.yaml`**: Deployment configuration for the API service.
- **`api-service.yaml`**: Service configuration for exposing the API service externally.
- **`frontend-deployment.yaml`**: Deployment configuration for the frontend service.
- **`frontend-service.yaml`**: Service configuration for exposing the frontend service.
- **`vectorizer-deployment.yaml`**: Deployment configuration for the vectorizer service.
- **`vectorizer-service.yaml`**: Service configuration for internal vectorizer communication.
- **`secrets.yaml`**: Stores sensitive API keys for OpenAI and Pinecone.
- **`configmap.yaml`**: Stores non-sensitive configuration data like environment variables.
- **`ingress.yaml`**: Manages external HTTP/HTTPS routing for the application.

---

### **`ansible/`**
Contains Ansible playbooks for automating Kubernetes setup and application deployment.

- **`inventory.yml`**: Defines the control plane and worker nodes for the Kubernetes cluster.
- **`deploy-kubernetes-cluster.yml`**: Sets up the Kubernetes cluster on GKE, including Flannel networking and node joining.
- **`deploy-application.yml`**: Deploys the application to the Kubernetes cluster by applying YAML configurations.

---

### **`ci-cd/`**
Houses the CI/CD pipeline configuration for automating testing and deployment.

- **`.github/workflows/ci-pipeline.yml`**: GitHub Actions workflow for CI/CD.
  - Runs unit tests, integration tests, and deploys to Kubernetes upon merging changes.
- **`tests/`**: Contains unit and integration tests for the application.
  - **`test_api.py`**: Tests API service functionality.
  - **`test_frontend.py`**: Tests frontend integration.
  - **`test_vectorizer.py`**: Tests vectorizer service functionality.
  - **`integration_test_api.py`**: Validates API endpoints with the database.
- **`coverage-report/`**: Stores code coverage reports for maintaining 70%+ test coverage.

---

### **`workflow/`**
Orchestrates the entire pipeline, ensuring tasks are executed in sequence.

- **`workflow_manager.py`**:
  - Executes services in order: data extraction → cleaning → vectorization → DVC tracking → API service.
  - Allows independent startup of the API service.
  - Logs all activities and errors to `workflow_manager.log`.

---

#### **`README.MD`**
Comprehensive documentation including:
- Setup instructions.
- Detailed container functionality.
- Steps to run the project using Docker Compose, Ansible, and Kubernetes.
- Troubleshooting and debugging tips.

---

### Notes

1. **Kubernetes Integration**:
   - Application components are deployed as scalable deployments with load balancers.
   - Ingress manages HTTP/HTTPS routing.

2. **CI/CD**:
   - GitHub Actions automates testing and deployment.
   - Ensures high code quality and fast iterations.

3. **Ansible Automation**:
   - Simplifies Kubernetes cluster setup and application deployment on GKE.

4. **Reproducibility**:
   - **DVC** ensures all processed data is tracked and versioned for reproducibility.

5. **Frontend & Backend Integration**:
   - The **`api-service/`** provides a seamless user experience by integrating the frontend and backend into a single Flask application.
