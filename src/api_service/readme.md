
# API Service for Frontend Integration

This is the API service for the user-facing frontend application, built with Flask. The service is tightly coupled with the HTML templates and serves as the core interface for backend operations.

---

## **Build and Run Instructions**

### Prerequisites
- Ensure Docker is installed on your system.
- Place the necessary `data/` directory with SQLite database files in the project root.

---

### **Steps to Build and Run**

1. **Navigate to the `api-service` Directory**
   ```bash
   cd src/api-service
   ```

2. **Build the Docker Image**
   ```bash
   docker build -t api_service_image .
   ```

3. **Run the Docker Container**
   ```bash
   docker run --rm -p 5000:5000 \
     -v $(pwd)/../../data:/app/data \
     api_service_image
   ```

   - The `-p 5000:5000` flag maps the Flask application to port `5000` on your localhost.
   - The `-v $(pwd)/../../data:/app/data` flag mounts the `data/` directory for SQLite database access.

---

## **Accessing the Application**

1. Open a browser and navigate to:
   ```
   http://localhost:5000
   ```

2. Interact with the application through the HTML-based frontend.

---

## **Development Notes**

### **Frontend Files**
- Templates (`HTML`) are stored in the `templates/` folder.
- Static files (e.g., CSS, JS, images) are stored in the `static/` folder.

### **Flask APIs**
- Main logic resides in `main.py`.
- Modify or add routes in `main.py` as necessary for additional functionality.

---

## **Environment Variables**

If additional environment variables are required for database or external APIs:
1. Create a `.env` file in the project root.
2. Export the variables in the Docker container.

Example:
```bash
export FLASK_ENV=development
export DATABASE_URL=sqlite:///instance/database.db
```

---

## **Common Issues**

### 1. **Port Already in Use**
   - If port `5000` is already in use, modify the `-p` flag:
     ```bash
     docker run --rm -p 5001:5000 api_service_image
     ```

### 2. **Missing Data Directory**
   - Ensure the `data/` directory exists and contains the required SQLite database.

---

## **Extending the Service**

### Adding New API Endpoints
1. Modify `main.py`.
2. Use the `Flask` routing syntax to define additional routes.

Example:
```python
@app.route('/new-endpoint', methods=['GET'])
def new_endpoint():
    return "New API Endpoint!"
```


