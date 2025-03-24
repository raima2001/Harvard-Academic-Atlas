## Purpose of Each Container

### **Data Extraction Container**

- **Purpose**: Scrapes course data from the Harvard Law School website and saves it to a CSV file in the `data/` directory.
- **Script**: `data_extraction.py`
- **Dependencies**:
  - `selenium`: For web automation.
  - `beautifulsoup4`: For parsing HTML.
  - **Note**: Uses Google Chrome and ChromeDriver for headless browsing.

### **Data Cleaning Container**

- **Purpose**: Cleans and processes the extracted data, exporting it to CSV, PDF, and DOCX formats in the `data/` directory.
- **Script**: `cleaning_data.py`
- **Dependencies**:
  - `pandas`: For data manipulation.
  - `fpdf`: For exporting PDFs.
  - `python-docx`: For exporting DOCX files.
  - `PyPDF2`: For reading PDFs.

### **Vectorizer Container**

- **Purpose**: Converts the cleaned data files into vector embeddings and interacts with Pinecone and OpenAI APIs for querying.
- **Script**: `pdf_docx_to_vector.py`
- **Dependencies**:
  - `pinecone-client`: For interacting with Pinecone vector database.
  - `openai`: For fetching embeddings and model interactions.
  - `PyPDF2`: For reading PDFs.
  - `python-docx`: For reading DOCX files.
- **Additional Components**:
  - **Embeddings Database**:
    - `db/chroma.sqlite3`: A snapshot of the vector embeddings of the HLS course catalogue data stored locally. This allows for faster access and querying without always relying on remote API calls to Pinecone.

### **DVC Service**

- **Purpose**: Manages data versioning using DVC (Data Version Control).
- **Functionality**:
  - Reads the cleaned data, interacts with the LLM, and logs prompts and responses to `data/logs/llm_interactions.log`.
  - Adds the `data/` directory to DVC tracking.
  - Commits changes to Git.
  - Pushes data to the remote storage.
- **Dependencies**:
  - `dvc`: For data versioning and management.
  - **Note**: Requires configuration of remote storage for data backups.

### **API Service**

- **Purpose**: Provides a Flask-based backend for APIs and serves the frontend application.
- **Frontend**: HTML, CSS, and JS files for user interaction.
- **Backend**: Python scripts for managing workflows, interacting with the database, and serving data.
- **Dependencies**:
  - `Flask`, `SQLAlchemy`: For backend logic and database management.

---

## Prerequisites

- **Docker** and **Docker Compose** installed on your machine.
- **API Keys** for OpenAI and Pinecone services.
- Internet connection for pulling Docker images and accessing APIs.

---

## Setup and Running the Project

### Step-by-Step Guide

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/ac215_masalachai.git
   cd ac215_masalachai/src
   ```

2. **Set Up Environment Variables**:

   Create a `.env` file in the `src/` directory:

   ```bash
   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_ENVIRONMENT=your_pinecone_environment
   ```

   Replace `your_openai_api_key`, `your_pinecone_api_key`, and `your_pinecone_environment` with your actual API keys and environment.

3. **Build the Docker Images**:

   ```bash
   docker-compose build
   ```

4. **Run the Services**:

   ```bash
   docker-compose up
   ```

   This will execute the services in sequence:

   - **Data Extraction**: Scrapes data and saves it to `data/courses_data_all_pages.csv`.
   - **Data Cleaning**: Processes the CSV and outputs cleaned data to `data/`.
   - **Vectorizer**: Reads the cleaned data, generates embeddings, and interacts with the APIs.
   - **DVC Service**: Tracks the data directory, commits changes, and pushes data to remote storage.
   - **API Service**: Set up the server, run the apis and host the frontend applciation.

5. **Access the Application**:

   Visit the web-applcation at: `http://localhost:5000`

---

## Individual Container Execution

If you prefer to run each container separately, you can do so as follows:

### Data Extraction

```bash
cd src/datapipeline/data_extraction
docker build -t data_extraction_image .
docker run --rm -v $(pwd)/../../../data:/app/data data_extraction_image
```

### Data Cleaning

```bash
cd src/datapipeline/cleaning_data
docker build -t cleaning_data_image .
docker run --rm -v $(pwd)/../../../data:/app/data cleaning_data_image
```

### Vectorizer

```bash
cd src/vectorizer
docker build -t vectorizer_image .
docker run --rm -v $(pwd)/../../data:/app/data \
  -e OPENAI_API_KEY=your_openai_api_key \
  -e PINECONE_API_KEY=your_pinecone_api_key \
  -e PINECONE_ENVIRONMENT=your_pinecone_environment \
  vectorizer_image
```

### DVC Service

```bash
cd src/dvc
docker build -t dvc_image .
docker run --rm -v $(pwd)/../../:/app \
  -v /path/to/dvc_remote_storage:/dvc_remote \
  dvc_image bash -c "
  cd /app &&
  dvc add data/ &&
  git add data.dvc .gitignore &&
  git commit -m 'Track data with DVC' &&
  dvc push
  "
```

Replace `/path/to/dvc_remote_storage` with the actual path to your DVC remote storage.

### API Service

```bash
cd src/api-service
docker build -t api_service_image .
docker run --rm -p 5000:5000 \
  -v $(pwd)/../../data:/app/data \
  -e FLASK_ENV=development \
  api_service_image
```

## Testing the API Service

Once the container is running:
1. Ensure that the `instance/site.db` SQLite database is correctly populated.
2. Use tools like Postman or curl to test the API endpoints.

Example API Test:
```bash
curl http://localhost:5000/api/endpoint
```

---

## Troubleshooting

- **Volume Mapping Issues**: Ensure that the volume paths in the `docker-compose.yml` and Docker run commands correctly map to your project's directories.

- **API Keys**: Verify that your API keys are correctly set in the `.env` file and that you have sufficient permissions and quota.

- **File Paths**: Make sure that all file paths in your scripts are relative to the working directory inside the containers (`/app/data/`).

- **Dependency Errors**: If you encounter dependency issues, ensure that all required packages are listed in the `Pipfile` for each service.

- **Docker Permissions**: If you encounter permission errors when accessing the `data/` directory, adjust the permissions or run Docker commands with appropriate privileges.

- **Contact the Collaborators**: If problems persist, reach out to the project collaborators for assistance.

