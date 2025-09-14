# Enhanced SciRAG Production Dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV SCIRAG_ENHANCED_PROCESSING=true
ENV SCIRAG_MATH_PROCESSING=true
ENV SCIRAG_ASSET_PROCESSING=true
ENV SCIRAG_GLOSSARY_EXTRACTION=true

# Set work directory
WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements-minimal.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p logs data cache temp markdown_files

# Set permissions
RUN chmod +x scripts/*.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "scirag.api.server"]
