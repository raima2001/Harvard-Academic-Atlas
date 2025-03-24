# Setup and Running the Project 🚀 - MS5

---

## **1️⃣ Create a GCP Account**
1. Sign in to the [Google Cloud Console](https://console.cloud.google.com/). 🌐
2. If you're new to GCP, activate the **Free Trial** to get $300 in credits. 💳

---

## **2️⃣ Create a New Project**
1. In the Cloud Console, navigate to **Manage Resources**.
2. Click **Create Project**, give it a meaningful name (e.g., `harvard-academic-atlas`), and select it after it's created.

---

## **3️⃣ Configure Kubernetes Cluster**
1. Go to **Kubernetes Engine** > **Clusters** in the Cloud Console.
2. Click **Create Cluster**.

### **Cluster Configuration**
- **Name**: `hls-advisor-cluster-1`.
- **Location Type**: Regional.
- **Region**: `us-central1`.
- **Node Configuration**:
  - **Machine Type**: `n2d-standard-2`.
  - **Disk Size**: 30 GB.
- **Pod Network CIDR**: `10.121.128.0/17`.
- Enable **HTTP/HTTPS traffic** under Networking.

---

## **4️⃣ Install gcloud and kubectl**
1. Install the Google Cloud CLI (`gcloud`) and Kubernetes CLI (`kubectl`) on your local machine:
   ```bash
   sudo apt update && sudo apt install -y google-cloud-sdk kubectl
   ```

2. Authenticate with GCP:
   ```bash
   gcloud auth login
   gcloud config set project <PROJECT_ID>
   ```

3. Connect to the cluster:
   ```bash
   gcloud container clusters get-credentials hls-advisor-cluster-1 --region us-central1
   ```

---

## **5️⃣ Configure a Virtual Machine (Optional)**
For deployment with Ansible or manual setups:
1. Go to **Compute Engine** > **VM Instances** and create a new VM.
2. Configure the instance as follows:
   - **Machine Type**: `e2-micro` (2 vCPUs, 1 GB RAM).
   - **Boot Disk**: Ubuntu 22.04 LTS.
   - Enable **HTTP/HTTPS traffic** under Networking.
3. SSH into the VM:
   ```bash
   gcloud compute ssh <INSTANCE_NAME> --zone <ZONE>
   ```

---

## **6️⃣ Install Docker and Ansible**
On your local machine or GCP VM:
1. **Install Docker**:
   ```bash
   sudo apt update && sudo apt install -y docker.io
   sudo usermod -aG docker ${USER}
   sudo systemctl enable docker
   ```

2. **Install Ansible**:
   ```bash
   sudo apt update && sudo apt install -y ansible
   ```

---

## **7️⃣ Clone the Repository**
1. Clone the project repository:
   ```bash
   git clone https://github.com/aditya-saxena-7/ac215_masalachai.git
   cd ac215_masalachai
   ```

---

## **8️⃣ Deployment Options**

### **Option 1: Run Locally with Docker Compose**
1. Navigate to the `src/` directory:
   ```bash
   cd src
   ```

2. Build the Docker images:
   ```bash
   docker-compose build
   ```

3. Start the services:
   ```bash
   docker-compose up
   ```

4. Access the application at:
   ```plaintext
   http://<EXTERNAL_IP>:5000
   ```

---

### **Option 2: Deploy on Kubernetes**
1. Build and push Docker images to **Google Container Registry (GCR)**:
   ```bash
   docker build -t gcr.io/<PROJECT_ID>/api-service:latest ./src/api-service
   docker push gcr.io/<PROJECT_ID>/api-service:latest
   ```

2. Apply Kubernetes configurations:
   ```bash
   kubectl apply -f kubernetes/
   ```

3. Verify the deployment:
   ```bash
   kubectl get pods
   kubectl get services
   kubectl get ingress
   ```

4. Access the application via the Nginx ingress IP:
   ```plaintext
   https://<Nginx Ingress IP>.sslip.io
   ```

---

### **Option 3: Automate Deployment with Ansible**
1. Update the Ansible inventory file (`ansible/inventory.yml`) with the GKE control plane and worker node IPs.
2. Run the playbook to set up the cluster:
   ```bash
   ansible-playbook -i ansible/inventory.yml ansible/deploy-kubernetes-cluster.yml
   ```

3. Deploy the application:
   ```bash
   ansible-playbook -i ansible/inventory.yml ansible/deploy-application.yml
   ```

4. Verify the deployment:
   ```bash
   kubectl get pods
   kubectl get services
   ```

---

## **9️⃣ Configure CI/CD Pipeline**
1. Add the environment variables for OpenAI and Pinecone in GitHub repository secrets.
2. GitHub Actions (`ci-pipeline.yml`) will:
   - Run unit and integration tests.
   - Deploy changes to the Kubernetes cluster on every `main` branch update.

---

## **🔍 Testing and Logs**

### **Kubernetes Logs**
Check logs for any pod:
```bash
kubectl logs <POD_NAME>
```

### **CI/CD Logs**
Monitor CI/CD pipeline execution in the **GitHub Actions** tab.

---

## **📋 Notes**

- Ensure **API keys** for OpenAI and Pinecone are securely stored in `.env` or Kubernetes secrets.
- Use **HTTPS** for secure communication, enabled via Nginx ingress and a self-signed TLS certificate.

---

# Setup and Running the Project 🚀 - MS4

This guide walks you through setting up and running the **`ac215_masalachai`** project on a **Google Cloud Platform (GCP)** Ubuntu Virtual Machine, equivalent to an AWS `t3.micro` instance.

---

## **1️⃣ Create a GCP Account**
1. Sign in to the [Google Cloud Console](https://console.cloud.google.com/). 🌐
2. If you're new to GCP, activate the **Free Trial** to get $300 in credits. 💳

---

## **2️⃣ Create a New Project**
1. In the Cloud Console, navigate to **Manage Resources**.
2. Click **Create Project**, give it a meaningful name, and select it after it's created.

---

## **3️⃣ Configure a Virtual Machine Instance**
1. Go to **Compute Engine** > **VM Instances**.
2. Click **Create Instance**.

### **Key Configuration:**
- **Name**: Enter a meaningful name for your instance.
- **Region**: Choose a region close to your target users or requirements (e.g., `us-east1` or `us-west1`).
- **Zone**: Select a zone within the region (e.g., `us-east1-b`).
- **Machine Configuration**:
  - **Series**: Select `E2`.
  - **Machine Type**: Choose `e2-micro`.  
    *Includes*: 
    - 2 vCPUs 🖥️
    - 1 GB RAM 🛠️
- **Boot Disk**:
  - **Operating System**: Ubuntu 🐧.
  - **Version**: Ubuntu 22.04 LTS.
  - **Boot Disk Size**: 10 GB (default, or adjust as needed).

---

## **4️⃣ Networking and Firewall Setup**
1. Scroll to the **Networking** section.
2. Under **Firewall**, check the boxes:
   - ✅ Allow HTTP traffic.
   - ✅ Allow HTTPS traffic.

---

## **5️⃣ Launch the Instance**
1. Review the configuration and click **Create**.
2. Wait for the instance to be provisioned. Once ready, it will appear in the VM Instances list.

---

## **6️⃣ Connect to the Instance**
1. In the VM Instances list, click **SSH** to open a terminal session directly in your browser. 💻
2. Alternatively, use the `gcloud` CLI:
   ```bash
   gcloud compute ssh <INSTANCE_NAME> --zone <ZONE>
   ```

---

## **7️⃣ Update and Install System Packages**
Once connected via SSH, update the system and install required packages:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip -y
```

---

## **8️⃣ Set Up Project Repository**
1. Clone the repository:
   ```bash
   git clone https://github.com/aditya-saxena-7/ac215_masalachai.git
   cd ac215_masalachai/src
   ```
2. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## **Advanced Configuration**

### **Set Up a Custom Domain with NGINX**
1. Install NGINX:
   ```bash
   sudo apt install nginx -y
   ```
2. Configure NGINX to route traffic:
   ```bash
   sudo nano /etc/nginx/sites-available/flask_app
   ```
   Add the following:
   ```plaintext
   server {
       listen 80;
       server_name <YOUR_DOMAIN>;
       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```
3. Enable the configuration:
   ```bash
   sudo ln -s /etc/nginx/sites-available/flask_app /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```

---

## **Docker Installation on GCP**
Follow these steps to install Docker on your GCP VM:

1. **Update the System**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Docker**:
   ```bash
   sudo apt install apt-transport-https ca-certificates curl software-properties-common -y
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
   sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
   sudo apt update
   sudo apt install docker-ce -y
   ```

3. **Test Docker Installation**:
   ```bash
   sudo docker run hello-world
   ```

4. **Enable Non-root Access** (Optional):
   ```bash
   sudo usermod -aG docker ${USER}
   su - ${USER}
   ```

5. **Enable Docker at Boot**:
   ```bash
   sudo systemctl enable docker
   ```

---

## **9️⃣ Configure Ports for the VM**
To allow external access to specific ports (e.g., `5000` for Flask):
1. Navigate to **VPC Network** > **Firewall** in the Cloud Console.
2. Click **Create Firewall Rule**.

### **Firewall Rule Configuration:**
- **Name**: `allow-flask`.
- **Network**: Select the VM’s network (default: `default`).
- **Priority**: Default.
- **Direction of Traffic**: **Ingress** (incoming traffic).
- **Action on Match**: **Allow**.
- **Target**: 
  - **All instances in the network**, or
  - **Specified target tags** (add the tag to your VM under **Network Tags** in the instance settings).
- **Source Filter**: **IP ranges** (`0.0.0.0/0` to allow all).
- **Protocols and Ports**: Enter `5000`.

Save the rule.

---

## **🔄 Running the Project**

### **1️⃣ Set Up Environment Variables**
Create a `.env` file in the `src/` directory:
```plaintext
OPENAI_API_KEY=<your_openai_api_key>
PINECONE_API_KEY=<your_pinecone_api_key>
PINECONE_ENVIRONMENT=<your_pinecone_environment>
```

---

### **2️⃣ Build Docker Images**
Navigate to the `src/` directory:
```bash
docker-compose build
```

---

### **3️⃣ Start the Services**
Run all services with Docker Compose:
```bash
docker-compose up
```

Services will run sequentially:
1. **Data Extraction**: Scrapes course data and saves it to `data/courses_data_all_pages.csv`. 📝
2. **Data Cleaning**: Processes raw data and exports cleaned outputs to `data/`. ✨
3. **Vectorizer**: Generates embeddings and interacts with Pinecone and OpenAI APIs. 🤖
4. **DVC Service**: Tracks data changes and pushes updates to remote storage. 📂
5. **API Service**: Starts the Flask API and serves the frontend. 🌐

---

## **4️⃣ Access the Application**
Visit the application at:
```plaintext
http://<EXTERNAL_IP>:5000
```

- Replace `<EXTERNAL_IP>` with your VM’s external IP address (visible in the Compute Engine dashboard).

---

## **🔍 Testing and Logs**

1. **Test Open Ports**:
   Run the Flask app to verify it listens on `0.0.0.0`:
   ```python
   app.run(host='0.0.0.0', port=5000)
   ```
2. **Logs**:
   Check logs for issues:
   ```bash
   docker logs <CONTAINER_NAME>
   ```

---

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
