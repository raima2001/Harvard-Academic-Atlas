**Directory Structure:**

```
ac215_masalachai/
├── data/                              # Tracked by DVC
│   ├── courses_data_all_pages.csv     # Extracted data
│   ├── HLS_cleaned_data.csv           # Cleaned data
│   ├── HLS_cleaned_data.pdf           # Cleaned data in PDF
│   ├── HLS_cleaned_data.docx          # Cleaned data in DOCX
│   └── logs/
│       └── llm_interactions.log       # LLM prompts and responses
│
├── reports/                           # Milestone 2 report and screenshots of the docker running locally
│
├── src/
│   ├── docker-compose.yml             # Docker Compose file for orchestration
│   ├── .env                           # Environment variables file with API keys
│
│   ├── datapipeline/
│   │   ├── data_extraction/
│   │   │   ├── Dockerfile             # Dockerfile for the data extraction container
│   │   │   ├── Pipfile                # Pipfile for package management
│   │   │   └── data_extraction.py     # Script for data extraction
│   │   │
│   │   ├── cleaning_data/
│   │   │   ├── Dockerfile             # Dockerfile for the data cleaning container
│   │   │   ├── Pipfile                # Pipfile for package management
│   │   │   └── cleaning_data.py       # Script for data cleaning
│
│   ├── vectorizer/
│   │   ├── Dockerfile                 # Dockerfile for the vectorizer container
│   │   ├── Pipfile                    # Pipfile for package management
│   │   └── pdf_docx_to_vector.py      # Script for vectorizing documents
│   │       ├── db/                    # Embeddings database directory
│   │           ├── chroma.sqlite3     # Snapshot of vector embeddings (HLS course catalogue data stored in Chroma Db)
│   │
│   ├── dvc/                           # Directory for DVC
│   │   └── Dockerfile                 # Dockerfile for DVC container
│   │
│   ├── .dvc/                          # DVC configuration directory
│   │   ├── config                     # DVC config file with remote storage settings
│   │
│   ├── data.dvc                       # DVC file tracking the data directory
│
├── README.MD
```

**Explanation of the Directory Structure:**

- **`ac215_masalachai/`**: The root directory of your project.

  - **`data/`**: A shared directory for data files, tracked by DVC. This directory is mounted into each Docker container to facilitate data sharing between different stages of your pipeline.

    - **`courses_data_all_pages.csv`**: The raw data extracted from the Harvard Law School website.
    - **`HLS_cleaned_data.csv`**: The cleaned and processed data.
    - **`HLS_cleaned_data.pdf`**: The cleaned data exported in PDF format.
    - **`HLS_cleaned_data.docx`**: The cleaned data exported in DOCX format.
    - **`logs/llm_interactions.log`**: Logs of interactions with the Large Language Model (LLM), including prompts and generated responses.

  - **`reports/`**: Contains the Milestone 2 report and screenshots of Docker running locally, documenting the project's progress and setup.

  - **`src/`**: Contains all source code and configuration files.

    - **`docker-compose.yml`**: The Docker Compose file that orchestrates the running of containers in the correct order and sets up the necessary environment variables and volume mounts.

    - **`.env`**: A file containing environment variables, such as API keys for OpenAI and Pinecone. This file is used by Docker Compose to inject environment variables into the containers.

    - **`datapipeline/`**: Directory containing data pipeline components.

      - **`data_extraction/`**: Contains the data extraction component.

        - **`Dockerfile`**: Defines the Docker image for the data extraction container.
        - **`Pipfile`**: Manages Python dependencies for the data extraction script.
        - **`data_extraction.py`**: The Python script that scrapes course data from the Harvard Law School website.

      - **`cleaning_data/`**: Contains the data cleaning component.

        - **`Dockerfile`**: Defines the Docker image for the data cleaning container.
        - **`Pipfile`**: Manages Python dependencies for the data cleaning script.
        - **`cleaning_data.py`**: The Python script that cleans and processes the extracted data.

    - **`vectorizer/`**: Contains the vectorizer component.

      - **`Dockerfile`**: Defines the Docker image for the vectorizer container.
      - **`Pipfile`**: Manages Python dependencies for the vectorizer script.
      - **`pdf_docx_to_vector.py`**: The Python script that converts documents into vector embeddings and interacts with Pinecone and OpenAIAzure (for text embeddings) APIs.
      - **`db/`**: Directory containing the embeddings database.

        - **`chroma.sqlite3`**: A snapshot of the vector embeddings of the HLS course catalogue data, stored using Chroma. This file serves as a local cache or backup of the embeddings that are also stored in Pinecone. (Please note we have used Pinecone for the docker but experimented with ChromaDb as well). It allows for faster access and querying of the embeddings without always relying on remote API calls to Pinecone.

    - **`dvc/`**: Directory for DVC (Data Version Control).

      - **`Dockerfile`**: Dockerfile for the DVC container, which handles data versioning tasks.

    - **`.dvc/`**: DVC configuration directory.

      - **`config`**: The DVC configuration file containing remote storage settings and other configurations.

    - **`data.dvc`**: The DVC file tracking the `data/` directory. It contains metadata about the data files, enabling version control and reproducibility.

  - **`README.MD`**: Project documentation, including setup instructions, usage guidelines, and other relevant information.

**Notes:**

- The `data/` directory is located at the root level (`ac215_masalachai/data/`) and is shared among all containers. Each container can read from and write to this directory, allowing data to flow through the pipeline stages.

- The `src/` directory contains all the source code and configuration necessary to build and run the containers.

- The `docker-compose.yml` file and `.env` file are located directly under `src/` to orchestrate the containers defined within the `src/` subdirectories.

- Each component (data extraction, data cleaning, vectorizer) has its own subdirectory within `src/` (either directly or under `datapipeline/`), and each contains its own `Dockerfile`, `Pipfile`, and script(s).

**How to Use This Structure:**

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

5. **Accessing the Data**:

   The output files will be in the `data/` directory:

   - `HLS_cleaned_data.csv`
   - `HLS_cleaned_data.pdf`
   - `HLS_cleaned_data.docx`

6. **Interacting with the Vectorizer**:

   The `vectorizer` container runs an interactive script. Follow the on-screen prompts to query the vector database.

   Example interaction:

   ```
   What would you like to do? Type 'query', 'delete', 'change', or 'exit':
   ```

   Type `query` to start querying the data.

---

**Additional Details:**

- **Individual Container Execution:**

  - If you prefer to run each component separately, you can navigate to each component's directory and build/run the Docker container individually. Remember to mount the `data/` directory appropriately so that data can be accessed.

- **Volume Mounts:**

  - The `data/` directory is mounted into the containers using Docker's volume feature. This allows the containers to read and write files to your host system, facilitating data sharing between components.

- **Environment Variables:**

  - The `.env` file is used by Docker Compose to inject API keys into the vectorizer container. Make sure this file is secure and not checked into version control if it contains sensitive information.

## Individual Container Execution

If you prefer to run each container separately, you can do so as follows:

**Example Commands for Individual Components:**

- **Data Extraction:**

  ```bash
  cd ac215_masalachai/src/datapipeline/data_extraction
  docker build -t data_extraction_image .
  docker run --rm -v $(pwd)/../../../data:/app/data data_extraction_image
  ```

- **Data Cleaning:**

  ```bash
  cd ac215_masalachai/src/datapipeline/cleaning_data
  docker build -t cleaning_data_image .
  docker run --rm -v $(pwd)/../../../data:/app/data cleaning_data_image
  ```

- **Vectorizer:**

  ```bash
  cd ac215_masalachai/src/vectorizer
  docker build -t vectorizer_image .
  docker run --rm -v $(pwd)/../../data:/app/data \
    -e OPENAI_API_KEY=your_openai_api_key \
    -e PINECONE_API_KEY=your_pinecone_api_key \
    -e PINECONE_ENVIRONMENT=your_pinecone_environment \
    vectorizer_image
  ```

---

## Screenshots

Below are screenshots showing Docker running locally with the model answering questions.

### 1. Docker Services Running

![Docker Services Running](https://github.com/aditya-saxena-7/ac215_masalachai/blob/milestone2/reports/2.jpeg)


![Interactive Query Prompt](https://github.com/aditya-saxena-7/ac215_masalachai/blob/milestone2/reports/3.jpeg)


## AWS EC2 Server Setup

1. **Instance Type**: Choose a `t3micro` for your EC2 instance.

### Initial Server Configuration
Once your EC2 instance is running, connect to it and perform the following steps:

1. **Update System Packages**:
    ```
    sudo apt update
    sudo apt upgrade
    ```
2. **Install Python and Pip**:
    ```
    sudo apt install python3-pip
    ```
3. **Install Required Python Packages (Optional)**:
    Clone your repository and install the required packages listed in `requirements.txt`:
    ```
    git clone <your-repository-url>
    cd <your-repository-directory>
    pip install -r requirements.txt
    ```

### GitHub Token Creation and Configuration
1. **Create a Personal Access Token**:
   - Go to GitHub settings under your account.
   - Navigate to [Personal Access Tokens](https://github.com/settings/personal-access-tokens/new).
   - Change the resource owner to `aditya-saxena-7`.
   - Select `All repositories` for repository access.
   - Generate the token and copy it for later use.

2. **Set Up Token on EC2 Server**:
   - Use the following commands to store your GitHub credentials:
     ```
     git config --global credential.helper store
     git clone <your-repository-url>
     ```
   - When prompted, enter your username and the personal access token you created.

### Server Configuration for Web Access
1. **Open Server Ports**:
   - Modify the Inbound Rules in the EC2 dashboard to allow traffic (e.g., Custom TCP 5000).

2. **Setting Up a Subdomain**:
   - Use AWS Route 53 to map your EC2 instance’s IP (e.g., 43.204.148.48) to a subdomain like `site_name`.

3. **Configure NGINX**:
   - Install and configure NGINX to redirect traffic to your application:
     ```
     sudo apt install nginx
     sudo vi /etc/nginx/sites-available/site_name.config
     ```
   - Paste the following server configuration into the file:
     ```
     server {
         listen 80;
         server_name site_name;
         client_max_body_size 100M;
         location / {
             proxy_pass http://localhost:5000;
             proxy_read_timeout 500s;
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
             proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
             proxy_set_header X-Forwarded-Proto $scheme;
         }
     }
     ```
   - Save the file and exit.
   - Enable the site and restart NGINX:
     ```
     sudo ln -s /etc/nginx/sites-available/site_name.config /etc/nginx/sites-enabled/
     sudo systemctl restart nginx
     ```

4. **Enable SSL with Let's Encrypt**:
   - Install Certbot and its Nginx plugin:
     ```
     sudo apt install certbot python3-certbot-nginx
     ```
   - Run Certbot for Nginx and follow the instructions:
     ```
     sudo certbot --nginx
     ```
   - Test automatic renewal:
     ```
     sudo certbot renew --dry-run
     ```
   - Restart NGINX to apply the SSL certificate:
     ```
     sudo systemctl restart nginx
     ```

### Start Your Application
- Finally, start your Python server. You can use `nohup` to keep it running in the background:

## Installing Docker

Installing Docker on an Ubuntu AWS server is a straightforward process. Here's a step-by-step guide to help you set it up:

1. **Update Your System**  
   Before installing Docker, it's a good idea to update your package listings to ensure you get the latest versions of packages.

   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

2. **Install Required Packages**  
   Install packages to allow `apt` to use a repository over HTTPS:

   ```bash
   sudo apt install apt-transport-https ca-certificates curl software-properties-common
   ```

3. **Add Docker’s Official GPG Key**  
   This ensures the software you're installing is authenticated and updates are received securely.

   ```bash
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   ```

4. **Set up the Stable Repository**  
   Add the Docker repository to APT sources:

   ```bash
   sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
   ```

5. **Install Docker CE (Community Edition)**  
   Update the `apt` package index, and install the latest version of Docker CE:

   ```bash
   sudo apt update
   sudo apt install docker-ce
   ```

6. **Verify Docker Installation**  
   Check that Docker is installed correctly by running the hello-world image:

   ```bash
   sudo docker run hello-world
   ```

   This command downloads a test image and runs it in a container. If the installation is correct, you will see a message indicating that Docker is installed correctly and running.

7. **Manage Docker as a Non-root User** (optional)  
   If you want to avoid typing `sudo` whenever you run the Docker command, add your username to the Docker group:

   ```bash
   sudo usermod -aG docker ${USER}
   su - ${USER}
   ```

   You will need to log out and back in for this to take effect, or you can type `su - ${USER}` to refresh your group membership.

8. **Configure Docker to Start on Boot**  
   Optionally, enable Docker to start at boot:

   ```bash
   sudo systemctl enable docker
   ```

That’s it! Docker should now be installed and ready to use on your Ubuntu server on AWS.

### **Troubleshooting:**

Contact the collaborators.
