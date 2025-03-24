**Build Instructions**:

1. Navigate to the `vectorizer` directory:

   ```bash
   cd src/vectorizer
   ```

2. Build the Docker image:

   ```bash
   docker build -t vectorizer_image .
   ```

3. Run the Docker container (provide your API keys):

   ```bash
   docker run --rm -v $(pwd)/../../data:/app/data \
     -e OPENAI_API_KEY=your_openai_api_key \
     -e PINECONE_API_KEY=your_pinecone_api_key \
     -e PINECONE_ENVIRONMENT=your_pinecone_environment \
     vectorizer_image
   ```

   **Overview**:

   - The `-v $(pwd)/../../data:/app/data` flag mounts the `data/` directory into the container.
   - Environment variables are passed using the `-e` flag.


