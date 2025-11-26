FROM python:3.11-slim

# Set working directory to parent
WORKDIR /workspace

# Copy requirements and install dependencies
COPY requirements.txt knowledge_base_app/
RUN pip install --no-cache-dir -r knowledge_base_app/requirements.txt

# Copy application code
COPY . knowledge_base_app/

# Expose port
EXPOSE 8000

# Run from parent directory with full module path
CMD ["uvicorn", "knowledge_base_app.main:app", "--host", "0.0.0.0", "--port", "8000"]