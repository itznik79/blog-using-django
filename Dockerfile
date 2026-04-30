# 1. Base image
FROM python:3.11-slim

# WHY:
# Lightweight Linux + Python preinstalled
# Slim = smaller image, faster build

# 2. Set working directory inside container
WORKDIR /app

# WHY:
# All commands will run inside /app
# Your project will live here

# 3. Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# WHY:
# Avoid unnecessary files → cleaner container

# 4. Prevent Python output buffering
ENV PYTHONUNBUFFERED=1

# WHY:
# Logs appear instantly (important for debugging)

# 5. Copy requirements first
COPY requirements.txt .

# WHY:
# Docker caching → dependencies won’t reinstall every time

# 6. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# WHY:
# Install Django + other packages

# 7. Copy project code
COPY . .

# 8. Default command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]