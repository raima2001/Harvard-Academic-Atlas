
# Workflow Manager Documentation

The `workflow_manager.py` script orchestrates the execution of various pipeline stages, ensuring sequential execution of data extraction, cleaning, vectorization, DVC tracking, and the API service. It can also start the API service independently.

---

## How `workflow_manager.py` Works

1. **Stage Definitions**:
   - Each stage corresponds to a Docker service defined in `docker-compose.yml`.
   - Stages are executed sequentially, resolving dependencies.

2. **Environment Variable Loading**:
   - Loads `.env` file to set required API keys and configurations.

3. **Docker Service Execution**:
   - Uses `subprocess.run` to invoke Docker services.
   - Logs outputs and errors for debugging.

4. **Error Handling**:
   - Stops workflow execution if any stage fails.
   - Logs all errors to `workflow_manager.log`.

5. **Menu for Workflow Options**:
   - Users can:
     1. Run the full workflow.
     2. Start the API service only.
     3. Exit the script.

---

## Steps to Run

1. **Navigate to the `workflow` Directory**:
   ```bash
   cd src/workflow
   ```

2. **Run the Workflow Manager**:
   ```bash
   python workflow_manager.py
   ```

3. **Choose an Option**:
   - **Option 1**: Run the full workflow (all stages).
   - **Option 2**: Start the API service independently.
   - **Option 3**: Exit the workflow manager.

---

## Example Usage

### **Run Full Workflow**
- Executes all stages sequentially:
  - `data_extraction`
  - `data_cleaning`
  - `vectorization`
  - `dvc_push`
  - `api_service`
    
- Output Example:
  ```bash
  Starting: Extracting data from Harvard Law School website
  Completed: Extracting data from Harvard Law School website

  Starting: Cleaning and processing the extracted data
  Completed: Cleaning and processing the extracted data

  Starting: Vectorizing cleaned data and storing embeddings
  Completed: Vectorizing cleaned data and storing embeddings

  Starting: Tracking and pushing data with DVC
  Completed: Tracking and pushing data with DVC

  Starting: Starting the Flask API and frontend service
  Completed: Starting the Flask API and frontend service

  Workflow completed. Check workflow_manager.log for details.
  ```

### **Start API Service Only**
- Skips data processing stages and starts the Flask API.
- Output Example:
  ```plaintext
  Starting the API service...
  Service api_service completed successfully.
  ```

---

## Log Location
All logs, including errors, are saved to:
```
workflow_manager.log
```

---

## Notes
- Ensure `docker-compose.yml` is correctly configured.
- The `.env` file should include:
  ```
  OPENAI_API_KEY=<your_openai_api_key>
  PINECONE_API_KEY=<your_pinecone_api_key>
  PINECONE_ENVIRONMENT=<your_pinecone_environment>
  ```
- Docker services must have network access to the required APIs.

--- 
