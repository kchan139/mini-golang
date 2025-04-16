FROM python:3.12-slim

# Install Java (required for ANTLR)
RUN apt-get update && \
    apt-get install -y default-jdk

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy ANTLR jar and set environment variable
COPY antlr-4.9.2-complete.jar .
ENV ANTLR_JAR=/app/antlr-4.9.2-complete.jar

# Set Python path for test modules
# ENV PYTHONPATH="/app"

# Default command (can be overridden)
CMD ["bash"] 