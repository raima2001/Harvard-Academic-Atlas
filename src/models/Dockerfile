# Use an official CUDA-enabled PyTorch base image
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TORCH_HOME=/app/torch_cache \
    HF_HOME=/app/huggingface_cache

# Create necessary directories
RUN mkdir -p /app/torch_cache /app/huggingface_cache /app/src

# Copy the entire repository to the container
COPY . /app/src/

# Set working directory to the src/models folder
WORKDIR /app/src/models

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install specific ML libraries
RUN pip install --no-cache-dir \
    transformers \
    datasets \
    peft \
    trl \
    accelerate \
    tensorboard \
    'torch>=2.0.0' \
    'torch_optimizer'

# Expose TensorBoard port
EXPOSE 6006

# Default command to run the training script
# Adjust the script name as needed
CMD ["python", "-u", "train_llama_model.py"]