# 📦 Base image Python 3.11 slim
FROM python:3.11-slim

# 🌍 Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# 📁 Set working directory
WORKDIR /app

# ⚙️ Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    gettext \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# 📦 Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 📦 Install Node.js dependencies
COPY package*.json ./
RUN npm install

# 📁 Copy project
COPY . .

# 🎨 Build frontend assets
RUN npm run build

# 📂 Collect static files
RUN python manage.py collectstatic --noinput

# 👤 Create and use non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# 🚪 Expose port
EXPOSE 8000

# 🚀 Run Gunicorn
CMD ["gunicorn", "-c", "gunicorn.conf.py", "lms_backend.wsgi:application"]
