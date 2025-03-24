**Build Instructions**:

1. Navigate to the `cleaning_data` directory:

   ```bash
   cd src/datapipeline/cleaning_data
   ```

2. Build the Docker image:

   ```bash
   docker build -t cleaning_data_image .
   ```

3. Run the Docker container:

   ```bash
   docker run --rm -v $(pwd)/../../../data:/app/data cleaning_data_image
   ```

   **Overview**:

   - The `-v $(pwd)/../../../data:/app/data` flag mounts the `data/` directory into the container.
   - Ensure that `cleaning_data.py` reads input files from `/app/data` and writes output files to `/app/data`.

