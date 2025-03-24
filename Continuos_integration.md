# 🔄 Continuous Integration and Deployment (CI/CD) with Coverage Setup

## Overview

This document details the CI/CD setup for the **Harvard Academic Atlas** project. The pipeline ensures automated testing, code coverage analysis, and deployment for every code push or pull request on the `main` branch.

---

## 📂 **Location of CI/CD Configuration**

The CI/CD configuration is defined in:

```bash
.github/workflows/ci-pipeline.yml
```

This YAML file specifies the GitHub Actions workflow for testing, code quality checks, and deployment.

---

## ⚙️ **Workflow Triggers**

The pipeline is triggered on the following events:

1. **Push Events**: Triggered whenever code is pushed to the `main` branch.
2. **Pull Requests**: Triggered whenever a pull request targeting the `main` branch is created or updated.

Trigger configuration in `ci-pipeline.yml`:

```yaml
on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
```

---

## 🛠️ **Key CI/CD Stages**

### 1. **Checkout Code**
The workflow starts by checking out the repository to the GitHub Actions runner. This step ensures that the latest code changes are available for subsequent stages.

```yaml
- name: Checkout code
  uses: actions/checkout@v3
```

---

### 2. **Set Up Python Environment**
A Python environment (version 3.12) is configured to match the project requirements.

```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: 3.12
```

---

### 3. **Install Dependencies**
Project dependencies listed in `requirements.txt` are installed using `pip`. This ensures all packages, including `pytest` and `pytest-cov`, are available for testing and coverage analysis.

```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
```

---

### 4. **Run Unit and Integration Tests**
Tests are executed using `pytest` to validate the application. Coverage reports are generated for the following directories:
- `src`
- `workflow`

Reports include:
- **Terminal Summary**: Logs test results directly in the GitHub Actions interface.
- **HTML Report**: Stored as an artifact for further analysis.

Environment variables are configured to include relevant directories in the `PYTHONPATH`.

```yaml
- name: Run Tests with Coverage
  env:
    PYTHONPATH: src:src/api_service:workflow
  run: |
    pytest tests --cov=src --cov=workflow --cov-report=term-missing --cov-report=html
```

---

### 5. **Upload Coverage Report**
The HTML coverage report is uploaded as a GitHub Actions artifact for easy access.

```yaml
- name: Upload Coverage Report
  uses: actions/upload-artifact@v3
  with:
    name: coverage-report
    path: htmlcov/
```

---

### 6. **Check Coverage Threshold**
Enforces a minimum coverage threshold of 70% to maintain code quality. The pipeline fails if the coverage is below the required threshold.

```yaml
- name: Check Coverage Threshold
  run: |
    coverage report --fail-under=70
```

---

### 7. **Build and Push Docker Images**
The pipeline builds Docker images for the `api-service`, `frontend`, and `vectorizer` components and pushes them to **Google Container Registry (GCR)**.

```yaml
- name: Build and Push Docker Images
  run: |
    docker build -t gcr.io/<PROJECT_ID>/api-service:latest ./src/api-service
    docker build -t gcr.io/<PROJECT_ID>/frontend:latest ./src/frontend
    docker build -t gcr.io/<PROJECT_ID>/vectorizer:latest ./src/vectorizer
    docker push gcr.io/<PROJECT_ID>/api-service:latest
    docker push gcr.io/<PROJECT_ID>/frontend:latest
    docker push gcr.io/<PROJECT_ID>/vectorizer:latest
```

---

### 8. **Deploy to Kubernetes**
After passing tests and meeting the coverage threshold, the application is deployed to a Kubernetes cluster. This stage applies the Kubernetes YAML files to the target cluster.

```yaml
- name: Deploy to Kubernetes
  run: |
    kubectl apply -f kubernetes/
```

---

## ✅ **Success Criteria**

The CI/CD pipeline is successful if:
1. All tests pass without errors.
2. Code coverage meets or exceeds the 70% threshold.
3. Docker images are successfully pushed to GCR.
4. The application is deployed to the Kubernetes cluster without issues.

---

## 📊 **Generated Artifacts**

- **Coverage Report**: An HTML version of the code coverage report, available as a downloadable artifact named `coverage-report`.
- **Deployed Application**: The updated application is accessible via the Nginx ingress controller.

---

## 🚀 **Future Improvements**

1. **Code Quality Checks**:
   - Integrate tools like `flake8` and `black` for style enforcement.
   - Add security scans using tools like `bandit` or `trivy`.

2. **Enhanced Coverage**:
   - Add coverage for untested modules to ensure all critical functionality is validated.
   - Extend integration tests to cover inter-service interactions.

3. **Environment-Specific Deployments**:
   - Include automated deployments to **staging** and **production** environments with approval workflows.

4. **Monitoring and Alerting**:
   - Integrate monitoring tools like Prometheus or Datadog.
   - Set up alerts for failed deployments or resource bottlenecks.

---

For any questions or issues regarding the CI/CD pipeline, feel free to contact the development team. 🎉
