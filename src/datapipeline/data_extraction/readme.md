**Build Instructions**:

1. Navigate to the `data_extraction` directory:

   ```bash
   cd src/datapipeline/data_extraction
   ```

2. Build the Docker image:

   ```bash
   docker build -t data_extraction_image .
   ```

3. Run the Docker container:

   ```bash
   docker run --rm -v $(pwd)/../../../data:/app/data data_extraction_image
   ```

   **Overview**:

   - The `-v $(pwd)/../../../data:/app/data` flag mounts the `data/` directory (located three levels up from the current directory) into the container's `/app/data` directory.
   - The script `data_extraction.py` should output the scraped data to `/app/data`.
