# Navigate to the root of your repository
cd /home/kumartanmaygcp/project/ac215_masalachai

# Create main files and directories
mkdir -p data
touch data/.gitkeep  # To keep the 'data' directory in version control

mkdir -p notebooks
touch notebooks/eda.ipynb

mkdir -p references

mkdir -p reports
touch reports/'Statement of Work_Sample.pdf'  # Use quotes for spaces

mkdir -p src/datapipeline
touch src/datapipeline/Dockerfile
touch src/datapipeline/Pipfile
touch src/datapipeline/Pipfile.lock
touch src/datapipeline/dataloader.py
touch src/datapipeline/docker-shell.sh
touch src/datapipeline/preprocess_cv.py
touch src/datapipeline/preprocess_rag.py

# Create Docker Compose file in the src directory
touch src/docker-compose.yml

# Create models directory and files within src
mkdir -p src/models
touch src/models/Dockerfile
touch src/models/docker-shell.sh
touch src/models/infer_model.py
touch src/models/model_rag.py
touch src/models/train_model.py
