# Ansible Deployment for Harvard Academic Atlas

This folder contains Ansible playbooks and configurations to automate the deployment of a Kubernetes cluster and the Harvard Academic Atlas application on Google Kubernetes Engine (GKE).

---

## Directory Structure

```
ansible/
├── inventory.yml                 # Inventory file for Kubernetes nodes
├── deploy-kubernetes-cluster.yml # Playbook to create and configure Kubernetes cluster
├── deploy-application.yml        # Playbook to deploy application YAML files to Kubernetes
```

---

## Explanation of Files

### 1. **`inventory.yml`**
- **Purpose**: Defines the master and worker nodes of the Kubernetes cluster.
- **Key Points**:
  - `gke-control-plane`: The Kubernetes control plane node (uses the public endpoint `34.55.37.64` from GKE).
  - `gke-node-pool`: The worker node(s) of the Kubernetes cluster (uses the private endpoint `10.128.0.4` from GKE).
  - Configures SSH access using the private key at `~/.ssh/id_rsa`.

---

### 2. **`deploy-kubernetes-cluster.yml`**
- **Purpose**: Sets up a Kubernetes cluster on GKE, including:
  - Installing Kubernetes and Docker.
  - Initializing the Kubernetes cluster on the control plane.
  - Configuring a pod network (Flannel).
  - Adding worker nodes to the cluster.
- **Key Points**:
  - Initializes the cluster with the CIDR range `10.121.128.0/17` as per the GKE configuration.
  - Uses the public endpoint of the control plane to join worker nodes.
- **Dependencies**: Requires SSH access to all nodes and a valid token/hash from `kubeadm init`.

---

### 3. **`deploy-application.yml`**
- **Purpose**: Deploys the Harvard Academic Atlas application to the Kubernetes cluster, including:
  - Secrets and ConfigMaps.
  - Deployments and services for the API, frontend, and vectorizer.
  - Ingress configuration for routing traffic.
- **Key Points**:
  - Assumes the Kubernetes YAML files are in the `kubernetes/` directory.
  - Copies these files to the control plane node before applying them.

---

## Prerequisites

### 1. **Google Cloud Setup**
- A GKE cluster must be created with the following details:
  - **Cluster Name**: `hls-advisor-cluster-1`
  - **Region**: `us-central1`
  - **Pod Network CIDR**: `10.121.128.0/17`
- Ensure that the control plane and worker nodes are accessible via SSH.

### 2. **Ansible Installation**
Install Ansible on your local machine:
```bash
sudo apt update && sudo apt install -y ansible
```

### 3. **Prepare the Inventory**
- Update `inventory.yml` with the IPs and SSH details of your Kubernetes control plane and worker nodes.

---

## Deployment Instructions

### Step 1: Define the Inventory
Update the `inventory.yml` file with:
- `ansible_host`: Replace with the IPs of your control plane and worker nodes.
- `ansible_user`: Replace with the SSH user (e.g., `ubuntu`).
- `ansible_ssh_private_key_file`: Path to your SSH private key.

### Step 2: Deploy the Kubernetes Cluster
Run the `deploy-kubernetes-cluster.yml` playbook to configure the Kubernetes cluster:
```bash
ansible-playbook -i inventory.yml deploy-kubernetes-cluster.yml
```

### Step 3: Deploy the Application
Run the `deploy-application.yml` playbook to deploy the application to the cluster:
```bash
ansible-playbook -i inventory.yml deploy-application.yml
```

---

## Verification

### Check Cluster Nodes
Verify the Kubernetes cluster is set up correctly:
```bash
kubectl get nodes
```

### Check Application Deployment
Verify that all application components are running:
```bash
kubectl get pods
kubectl get services
kubectl get ingress
```

---

## Troubleshooting

### SSH Access Issues
- Ensure the private key path in `inventory.yml` is correct.
- Verify that the control plane and worker nodes allow SSH access.

### Kubernetes Errors
- Check logs on the control plane node:
  ```bash
  kubectl logs <pod-name>
  ```
- Ensure the Flannel network plugin is installed:
  ```bash
  kubectl get pods -n kube-system
  ```

### Application Errors
- Verify the application pods are running:
  ```bash
  kubectl get pods
  ```
- Check the ingress routes for proper traffic routing:
  ```bash
  kubectl describe ingress
  ```

---

## Notes

1. **Cluster Access**:
   - The cluster is configured to use the public endpoint for remote management (`34.55.37.64`).
   - Internal communication uses the private endpoint (`10.128.0.4`).

2. **Scalability**:
   - The cluster supports autoscaling based on the configuration in GKE.

3. **Future Enhancements**:
   - Integrate more robust error handling and monitoring tools (e.g., Prometheus).
   - Add support for automated certificate renewal for HTTPS.

