## **Build the DVC Docker Image**

Navigate to the `src/dvc` directory and build the Docker image:

```bash
cd src/dvc
docker build -t dvc_image .
```

## **Initializing DVC in the Project**

#### **1. Initialize a Git Repository**

If the project isn't already a Git repository, initialize it:

```bash
cd ac215_masalachai  
git init
git add .
git commit -m "Initial commit"
```

**Note**: If your project is already under version control, you can skip this step.

#### **2. Initialize DVC**

Run the DVC initialization inside the Docker container:

```bash
docker run -it --rm -v $(pwd):/app dvc_image
```

---

**Explanation of DVC (Data Version Control):**

DVC (Data Version Control) is a version control system specifically designed for handling large datasets and machine learning projects. It allows us to version control data and model files, similar to how Git manages code, but with a focus on large files that aren't practical to store in traditional Git repositories. DVC enables seamless collaboration on data-driven projects by providing a system to track and manage data versions, pipelines, and experiments.

**Why DVC is Useful:**

1. **Efficient Data Tracking**: DVC enables tracking changes in large datasets and managing multiple versions, making it easier to revert to previous versions if needed.
2. **Data Reproducibility**: It ensures that data transformations and model training steps can be reproduced exactly, which is critical for research and data science.
3. **Collaboration**: DVC provides remote storage capabilities, allowing collaborators to pull specific data versions without sharing entire datasets directly.
4. **Pipeline Management**: DVC tracks the workflow pipeline from data extraction to model deployment, making it easier to manage and automate complex pipelines.

**How We Used DVC in Our Project:**

In this project, we used DVC to manage the data directory (`data/`) and track data changes across our pipeline. Here’s how:

- **Data Tracking**: All raw and processed datasets (e.g., `courses_data_all_pages.csv`, `HLS_cleaned_data.csv`) in the `data/` directory are tracked by DVC. We created a DVC file (`data.dvc`) to keep version control on these files.
  
- **Pipeline Stages**: Each stage of our pipeline—data extraction, cleaning, and embedding—outputs data that is tracked by DVC. This ensures each step’s output is versioned, which is critical for reproducibility.
  
- **Remote Storage**: DVC allows us to set up remote storage (e.g., AWS S3 or Google Drive) to store data versions without overloading the local repository. This makes it easy to share updated data versions across collaborators.

By using DVC, we ensure that all our data files are version-controlled, trackable, and reproducible, even as the project evolves.
