# ✅ Use official slim image
FROM python:3.10-slim

# Set env variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements from the current folder
COPY ./requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy rest of the backend code
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
