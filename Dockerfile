# Stage 1: Base build stage
FROM python:3.12-slim AS builder
 
# Create the app directory
RUN mkdir /app
 
# Set the working directory
WORKDIR /app
 
# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 
 
# Install dependencies first for caching benefit
RUN pip install --upgrade pip 
COPY requirements.txt /app/ 
RUN pip install --no-cache-dir -r requirements.txt
 
# Stage 2: Production stage
FROM python:3.12-slim
 
RUN useradd -m -r db_user && \
   mkdir /app && \
   mkdir /app/staticfiles && \
   chown -R db_user:db_user /app
 
# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
 
# Set the working directory
WORKDIR /app
 
# Copy application code
COPY --chown=db_user:db_user . .
 
# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 
 
# Switch to non-root user
USER db_user
 
# Expose the application ports
EXPOSE 8000 8002

# Make entry files executable
RUN chmod +x  /app/entrypoint.prod.sh
RUN chmod +x  /app/entrypoint.websocket.sh
 
# Start the application using Gunicorn
CMD ["/app/entrypoint.prod.sh"]



















# FROM python:3.12-slim

# WORKDIR /app

# RUN apt-get update && apt-get install -y \
#     python3-dev \
#     python3-psycopg2 \
#     postgresql-client \
#     && rm -rf /var/lib/apt/lists/*

# COPY requirements.txt .
# RUN pip install -r requirements.txt

# COPY . .

# EXPOSE 8000

# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
