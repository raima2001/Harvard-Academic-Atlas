# Kubernetes Deployment Configuration

This directory contains the Kubernetes configuration files required to deploy and manage the **Harvard Academic Atlas** application on a Kubernetes cluster. The files include deployments, services, secrets, and other necessary configurations for running the application components efficiently on Google Kubernetes Engine (GKE).

---

## Directory Structure

```
kubernetes/
├── api-deployment.yaml          # Deployment file for API service
├── api-service.yaml             # Service file for API service
├── frontend-deployment.yaml     # Deployment file for the frontend
├── frontend-service.yaml        # Service file for the frontend
├── vectorizer-deployment.yaml   # Deployment file for the vectorizer
├── vectorizer-service.yaml      # Service file for the vectorizer
├── secrets.yaml                 # Kubernetes secrets for sensitive data
├── configmap.yaml               # ConfigMap for environment variables
├── ingress.yaml                 # Ingress configuration for routing traffic
├── tls-cert-secret.yaml         # TLS certificate secret for HTTPS
```

---

## Explanation of Files

### 1. **`api-deployment.yaml`**
- **Purpose**: Defines the deployment for the API service, including the number of replicas, container image, environment variables, and volumes.
- **Key Points**:
  - Uses the container image `gcr.io/ac-215-hw2/api-service:latest`.
  - Scales horizontally with 3 replicas.
  - Mounts a PersistentVolumeClaim (`api-service-data-pvc`) for storing persistent data.

### 2. **`api-service.yaml`**
- **Purpose**: Creates a `LoadBalancer` service for the API service, exposing it on port `5000`.
- **Key Points**:
  - Ensures external accessibility via a public IP.
  - Routes traffic to pods labeled `app: api-service`.

### 3. **`frontend-deployment.yaml`**
- **Purpose**: Defines the deployment for the frontend application.
- **Key Points**:
  - Uses the container image `gcr.io/ac-215-hw2/frontend:latest`.
  - Configures 2 replicas for high availability.
  - Exposes port `80` for the frontend application.

### 4. **`frontend-service.yaml`**
- **Purpose**: Creates a `NodePort` service for the frontend, exposing it on port `80`.
- **Key Points**:
  - Allows access to the frontend application through a specific node port.

### 5. **`vectorizer-deployment.yaml`**
- **Purpose**: Defines the deployment for the vectorizer service.
- **Key Points**:
  - Uses the container image `gcr.io/ac-215-hw2/vectorizer:latest`.
  - Configures environment variables for API keys from `secrets.yaml` and `configmap.yaml`.
  - Exposes port `8080`.

### 6. **`vectorizer-service.yaml`**
- **Purpose**: Creates a `ClusterIP` service for the vectorizer, making it available internally in the cluster.
- **Key Points**:
  - Routes traffic to pods labeled `app: vectorizer`.

### 7. **`secrets.yaml`**
- **Purpose**: Stores sensitive information like API keys for OpenAI and Pinecone.
- **Key Points**:
  - Data is stored in base64-encoded format.
  - Secures access to external APIs by passing secrets as environment variables.

### 8. **`configmap.yaml`**
- **Purpose**: Stores non-sensitive configuration data, such as the environment for Pinecone.
- **Key Points**:
  - Decouples configuration from the application, making it easier to manage and update.

### 9. **`ingress.yaml`**
- **Purpose**: Configures ingress routing for HTTP/HTTPS traffic, directing it to appropriate services based on the host or path.
- **Key Points**:
  - Uses `frontend.ac-215-hw2.example.com`, `api.ac-215-hw2.example.com`, and `vectorizer.ac-215-hw2.example.com` as hostnames.
  - Implements SSL termination using `tls-cert-secret.yaml`.

### 10. **`tls-cert-secret.yaml`**
- **Purpose**: Provides a TLS certificate for securing HTTPS connections.
- **Key Points**:
  - Contains base64-encoded certificate and private key data.
  - Used in the `ingress.yaml` for SSL termination.

---

## Steps to Run

### 1. **Set Up Google Kubernetes Engine (GKE)**
- Install and configure the `gcloud` CLI.
- Create a Kubernetes cluster:
  ```bash
  gcloud container clusters create ac-215-cluster --num-nodes=3 --zone=us-central1-a
  ```

### 2. **Push Docker Images to Google Container Registry**
- Build and push the required Docker images for the services:
  ```bash
  docker build -t gcr.io/ac-215-hw2/api-service:latest ./src/api-service
  docker push gcr.io/ac-215-hw2/api-service:latest

  docker build -t gcr.io/ac-215-hw2/frontend:latest ./src/frontend
  docker push gcr.io/ac-215-hw2/frontend:latest

  docker build -t gcr.io/ac-215-hw2/vectorizer:latest ./src/vectorizer
  docker push gcr.io/ac-215-hw2/vectorizer:latest
  ```

### 3. **Apply Kubernetes Configurations**
- Apply the configuration files in sequence:
  ```bash
  kubectl apply -f secrets.yaml
  kubectl apply -f configmap.yaml
  kubectl apply -f api-deployment.yaml
  kubectl apply -f api-service.yaml
  kubectl apply -f frontend-deployment.yaml
  kubectl apply -f frontend-service.yaml
  kubectl apply -f vectorizer-deployment.yaml
  kubectl apply -f vectorizer-service.yaml
  kubectl apply -f tls-cert-secret.yaml
  kubectl apply -f ingress.yaml
  ```

### 4. **Verify Deployment**
- Check the status of pods, services, and ingress:
  ```bash
  kubectl get pods
  kubectl get services
  kubectl get ingress
  ```

### 5. **Access the Application**
- Use the public IP or hostname of the services exposed by the `ingress.yaml`.

---

## Troubleshooting

1. **Pod Errors**:
   - Check logs for errors:
     ```bash
     kubectl logs <pod-name>
     ```

2. **Ingress Not Working**:
   - Ensure the ingress controller is installed and running:
     ```bash
     kubectl get pods --namespace ingress-nginx
     ```

3. **API Key Issues**:
   - Verify that the secrets are correctly encoded and applied:
     ```bash
     kubectl describe secret api-secrets
     ```

4. **Service Connectivity**:
   - Test internal connectivity:
     ```bash
     kubectl exec -it <pod-name> -- curl http://vectorizer:8080
     ```

---

## Notes

- Replace placeholders like `<pod-name>` or `gcr.io/ac-215-hw2` with actual values as per your setup.
- Use self-signed certificates or a valid certificate for `tls-cert-secret.yaml` depending on your use case.
