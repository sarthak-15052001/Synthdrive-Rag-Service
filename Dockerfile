FROM python:3.10-slim
 
# Set working directory
WORKDIR /app
 
# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy the rest of the application
COPY . .
 
# Set src as the Python path so Python can find your modules
ENV PYTHONPATH=/app/src
 
# Expose API port
EXPOSE 8001
 
# Run the API server
# Assuming your FastAPI app is in src/main.py as 'app'
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]