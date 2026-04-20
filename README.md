**Directory Structure (Milestone 5):**

```
ac215_masalachai/
├── data/                                 # Tracked by DVC
│   ├── courses_data_all_pages.csv        # Extracted data
│   ├── HLS_cleaned_data.csv              # Cleaned data
│   ├── HLS_cleaned_data.pdf              # Cleaned data in PDF
│   ├── HLS_cleaned_data.docx             # Cleaned data in DOCX
│   └── logs/
│       └── llm_interactions.log          # LLM prompts and responses
│
├── vault/                                # Milestone 4 images and screenshots used
│
├── src/
│   ├── docker-compose.yml                # Docker Compose file for orchestration
│   ├── .env                              # Environment variables file with API keys
│   │
│   ├── datapipeline/
│   │   ├── data_extraction/
│   │   │   ├── Dockerfile                # Dockerfile for the data extraction container
│   │   │   ├── Pipfile                   # Pipfile for package management
│   │   │   └── data_extraction.py        # Script for data extraction
│   │   │
│   │   ├── cleaning_data/
│   │   │   ├── Dockerfile                # Dockerfile for the data cleaning container
│   │   │   ├── Pipfile                   # Pipfile for package management
│   │   │   └── cleaning_data.py          # Script for data cleaning
│   │
│   ├── vectorizer/
│   │   ├── Dockerfile                    # Dockerfile for the vectorizer container
│   │   ├── Pipfile                       # Pipfile for package management
│   │   └── pdf_docx_to_vector.py         # Script for vectorizing documents
│   │       ├── db/                       # Embeddings database directory
│   │           ├── chroma.sqlite3        # Snapshot of vector embeddings (HLS course catalogue data stored in Chroma Db)
│   │
│   ├── dvc/                              # Directory for DVC
│   │   ├── Dockerfile                    # Dockerfile for DVC container
│   │
│   ├── .dvc/                             # DVC configuration directory
│   │   ├── config                        # DVC config file with remote storage settings
│   │
│   ├── data.dvc                          # DVC file tracking the data directory
│   │
│   ├── api-service/                      # API and frontend integration folder
│   │   ├── Dockerfile                    # Dockerfile for the Flask API service
│   │   ├── Pipfile                       # Pipfile for managing dependencies
│   │   ├── Pipfile.lock                  # Locked dependency versions
│   │   ├── main.py                       # Flask app with API routes and backend logic
│   │   ├── requirements.txt              # Requirements file for the Flask app
│   │   ├── instance/
│   │   │   └── site.db                   # SQLite database file
│   │   ├── templates/                    # Frontend HTML templates
│   │   │   ├── index.html                # Home page
│   │   │   └── and more HTML files    
│   │   │   
│   │   ├── static/                    
│   │   │   └── images/                   # Static Images
│   │   ├── py_files/                     # Additional Backend Python scripts
│   │   ├── knowledgebase/                # Student Resource Vault files
│   │   ├── chat_emails/                  # Email logs for interactions
│   │
│   ├── workflow/                         # Workflow orchestration logic
│   │   └── workflow_manager.py           # Orchestrates tasks across components
│   │
│   ├── kubernetes/                       # Kubernetes configurations and YAML files (new)
│   │   ├── api-deployment.yaml           # Deployment file for API service
│   │   ├── api-service.yaml              # Service file for API service
│   │   ├── frontend-deployment.yaml      # Deployment file for frontend
│   │   ├── frontend-service.yaml         # Service file for frontend
│   │   ├── vectorizer-deployment.yaml    # Deployment file for vectorizer
│   │   ├── vectorizer-service.yaml       # Service file for vectorizer
│   │   ├── secrets.yaml                  # Kubernetes secrets for sensitive data (e.g., API keys)
│   │   ├── configmap.yaml                # Kubernetes ConfigMap for environment variables
│   │   ├── ingress.yaml                  # Ingress file for HTTP/HTTPS routing
│   │
│   ├── ansible/                          # Ansible playbooks for automated deployment (new)
│   │   ├── inventory.yml                 # Hosts inventory file
│   │   ├── deploy-kubernetes-cluster.yml # Creates and configures a Kubernetes cluster
│   │   ├── deploy-application.yml        # Deploys application YAML files to Kubernetes
│   │
│   ├── ci-cd/                            # CI/CD pipeline configuration (new)
│       ├── .github/
│       │   ├── workflows/
│       │       ├── ci-pipeline.yml       # GitHub Actions CI/CD pipeline
│       │
│       ├── tests/
│           ├── teser_api.py
│           ├── test_api.py
│           ├── test_emails.py
│           ├── test_model_endpoint.py
│           ├── test_others.py
│           ├── val_key.py
│       ├── coverage-report/              # Stores test coverage reports
│
├── README.MD                             # Project documentation
```

# Harvard Academic Atlas Documentation

---

## **General Section**

- **Website**: [http://104.198.147.52:5000/](http://104.198.147.52:5000/)  
  Access the live Harvard Academic Atlas application.  

- **Website Navigation**: [Harvard Academic Atlas Guide](https://upskillrai.notion.site/Harvard-Academic-Atlas-Powered-by-MasalaChai-15469993f9f28013af95f8c64c9c54a9)  
  A comprehensive guide to the website’s features and navigation.

- **Medium Blog**: [Read More on Medium](https://medium.com/)  
  In-depth articles and insights into the development and use cases of the Harvard Academic Atlas.

---

## **GitHub Documentation**

1. **[Setup and Running the Project](https://github.com/aditya-saxena-7/ac215_masalachai/blob/milestone4/SetupandRunningtheProject.md)** 🚀  
   Step-by-step instructions to deploy and run the project locally or on a cloud server.

2. **[Explanation of the Directory Structure](https://github.com/aditya-saxena-7/ac215_masalachai/blob/milestone4/DirectoryStructureExplanation.md)** 📂  
   Detailed breakdown of the project's directory structure and its components.

3. **[API Documentation of Harvard Academic Atlas](https://github.com/aditya-saxena-7/ac215_masalachai/blob/milestone4/API_Documentation.md)** 📡  
   Comprehensive API documentation for seamless integration and usage.

4. **[Continuous Integration Setup](https://github.com/aditya-saxena-7/ac215_masalachai/blob/milestone4/Continuos_integration.md)** 🔄  
   Details on setting up CI pipelines for automated builds and deployments.

5. **[Automated Testing Implementation/Test Documentation](https://github.com/aditya-saxena-7/ac215_masalachai/blob/milestone4/test.md)** 🧪  
   Guidelines and examples of automated testing for the platform.

6. **[Application and Technical Architecture](https://github.com/aditya-saxena-7/ac215_masalachai/blob/milestone4/tech_archi.md)** 🏗️  
   Detailed design and workflow descriptions, and architectural guidelines for understanding the platform.

7. **[Live Web Application Tutorial](https://github.com/aditya-saxena-7/ac215_masalachai/blob/milestone4/ApplicationTutorial.md)** 🌐  
   Step-by-step guide on how to use the live application effectively.

---

## **YouTube Section**

Watch our video tutorials to explore the features of the Harvard Academic Atlas:

- **[Signup](https://youtu.be/MbkXsEcE2yc)** 🎥  
  Learn how to create an account on the platform.

- **[Login](https://youtu.be/GahCYVxkMqM)** 🎥  
  Walkthrough of the login process for existing users.

- **[HLS Academic Advisor](https://youtu.be/p8d7PqVusL8)** 🎥  
  Demonstration of the academic advising features powered by the platform.

- **[AC215 Showcase](https://youtu.be/SjQzYTbj5og)** 🎥  
  Overview of the project presented as part of the AC215 showcase.

- **[AC215 Final Video Presentation](https://youtu.be/oPg7MJ51P0E)** 🎥  
  Final 6 Minute Video Presentation by Team MasalaChai


