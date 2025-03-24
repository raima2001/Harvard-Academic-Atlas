# Model Architecture

## Solution Architecture

The solution architecture highlights the workflow and components used to create, deploy, and scale the **Harvard Academic Atlas** application, focusing on the process, execution, and state management layers. The inclusion of **Kubernetes** and **Ansible** enhances scalability and automation in deployment.

![image_1](https://github.com/aditya-saxena-7/ac215_masalachai/blob/milestone4/Solution%20Architecture%20Harvard%20Academia%20Atlas.png)

---

### **Process Layer**
1. **Develop App**:  
   - The team builds and maintains the application, integrating components like backend, frontend, and LLM/RAG pipelines.  
   - Kubernetes deployment configurations and Ansible playbooks are prepared to automate scaling and setup.

2. **ML Tasks**:  
   - Machine learning tasks include:
     - Data processing
     - Embedding generation
     - Model training/finetuning for specific course recommendation tasks  
   - Kubernetes ensures the ML pipeline scales dynamically to handle increased workload.

3. **Ask Crimson LLM**:  
   - Users interact with the app to get course recommendations using the Crimson LLM.  
   - Kubernetes ingress manages external access, and autoscaling ensures a seamless experience for multiple users.

---

### **Execution Layer**
1. **Notebooks**:  
   - Prototyping and experimentation are carried out in Jupyter or Colab notebooks, accessible via HTTPS/SSH.

2. **RAG Pipeline (Retrieval-Augmented Generation)**:
   - **Key Processes**:
     - Data is scraped from the Harvard Law School (HLS) catalog.
     - Data embeddings are stored in a vector store for efficient retrieval.
     - Kubernetes ensures pipeline components like the vectorizer and API services are highly available.

3. **LLM Pipeline**:  
   - Handles the lifecycle of machine learning models:
     - **Data Extraction & Preprocessing**: Prepares data extraction using Beautiful Soup and Selenium and uses Pandas to complete the data preprocessing.
     - **Model Training and Fine-Tuning**: Adjusts the base model and fine-tuned models to specific use cases like course recommendations.
     - **Model Deployment**: Deploys the trained model for use in the application in Google Cloud Platform, orchestrated via Kubernetes and Ansible.

4. **Frontend**:  
   - The Harvard Academia Atlas provides a user-friendly interface for interacting with the Crimson LLM.  
   - Kubernetes deployments ensure the frontend remains responsive even during high traffic.

5. **Backend**:  
   - The backend API service manages communication between the frontend and the LLM models.
   - Kubernetes services and ingress ensure secure data transfer and balanced load distribution.

---

### **State Layer**
1. **Source Control**:  
   - Manages version control for code repositories using tools like GitHub.

2. **Container Registry**:  
   - Stores Docker container images for deployment to Kubernetes.

3. **Vector Store**:  
   - Stores embeddings generated during the RAG pipeline for fast retrieval.

4. **GCS Bucket**:  
   - Securely hosts processed data and trained machine learning models for access during pipeline execution and deployment.

5. **Model Store**:  
   - Manages deployed models to ensure accessibility for inference tasks.

6. **Kubernetes Secrets**:
   - Protects sensitive API keys (e.g., OpenAI and Pinecone) and environment variables during runtime.

---

# Technical Architecture

The technical architecture delves into the infrastructure and interactions between services, focusing on deployment automation, scalability, and efficient resource management through Kubernetes and Ansible.

![image_2](https://github.com/aditya-saxena-7/ac215_masalachai/blob/milestone4/Technical%20Architecture%20-%20HAA.jpg)

---

## **Developers Layer**
1. **IDE/CLI**:
   - Developers use IDEs (e.g., VS Code) and CLI tools to write, test, and manage code.
   - Containers simulate production environments locally before deployment to Kubernetes.

2. **Source Control**:
   - GitHub is used for version control, CI/CD pipeline configuration, and collaborative development.

3. **Colab**:
   - Provides a platform for collaborative prototyping and development of machine learning models.

---

## **Google Cloud Platform (GCP)**
1. **Google Container Registry**:
   - Stores containerized components such as:
     - **Scraper Image**: Handles data scraping.
     - **API Service Image**: Manages API endpoints.
     - **Frontend Image**: Hosts the web interface for the application.
     - **Vectorizer Image**: Processes cleaned data and generates embeddings.

2. **Kubernetes Cluster**:
   - Orchestrates the deployment and scaling of application components, such as:
     - **Frontend Service**: Exposes the frontend through an Nginx ingress.
     - **API Service**: Handles backend logic and integrates with vectorizer and LLM pipelines.
     - **Vectorizer Service**: Generates embeddings and interacts with Pinecone and OpenAI APIs.

3. **GCS Bucket**:
   - Stores datasets, cleaned data, and intermediate results.

---

## **Ansible Integration**
1. **Kubernetes Cluster Automation**:
   - Ansible playbooks configure GKE clusters, ensuring consistent deployment and environment setup.
   - Automates:
     - Node provisioning
     - Cluster initialization
     - Flannel networking setup

2. **Application Deployment**:
   - Automates the application deployment by applying Kubernetes YAML files for:
     - Secrets
     - ConfigMaps
     - Deployments and services
     - Ingress for traffic routing

3. **Scalability**:
   - Ensures nodes and pods scale dynamically with cluster workloads.

---

## **Vertex AI**
1. **Data Scraper**:
   - Collects raw data for training and analysis.

2. **Data Processor**:
   - Preprocesses and cleans data for use in model training.

3. **Model Training**:
   - Trains machine learning models using preprocessed data.

---

## **Single Compute Instance/Kubernetes Cluster**
1. **NGINX Ingress**:
   - Manages external HTTP/HTTPS traffic and balances loads across services.

2. **Frontend Deployment**:
   - Hosts the user-facing application and interacts with the API.

3. **API Service Deployment**:
   - Handles backend logic, querying, and secure data access.

4. **Vectorizer Deployment**:
   - Manages vector embeddings and interaction with third-party APIs.

5. **Persistent Volumes**:
   - Ensures data persistence for critical services like the API and vectorizer.

---

## **Users Layer**
1. **Browser**:
   - End-users interact with the application through a browser interface, facilitated by Nginx ingress.
   - Traffic is routed securely via HTTPS using Kubernetes-managed TLS certificates.
