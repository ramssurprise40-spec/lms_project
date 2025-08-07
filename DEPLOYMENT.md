# LMS Deployment Guide

This guide covers how to deploy the Learning Management System (LMS) to production.

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 13+ (recommended) or MySQL 8.0+
- Redis 6+ (for caching and background tasks)
- Nginx (for reverse proxy)

## Quick Start with Docker (Recommended)

The easiest way to deploy the LMS is using Docker Compose:

1. **Clone the repository and navigate to the project directory**
2. **Copy environment configuration:**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` file with your configuration:**
   - Set `DEBUG=False`
   - Generate a secure `SECRET_KEY`
   - Configure your `GEMINI_API_KEY` for AI features
   - Set your email configuration
   - Configure other settings as needed

4. **Build and start the services:**
   ```bash
   docker-compose up -d
   ```

5. **Run initial setup:**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

6. **Access your LMS:**
   - Web interface: http://localhost:8000
   - Admin interface: http://localhost:8000/admin

## Manual Deployment

### 1. Server Setup

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip nodejs npm postgresql redis-server nginx
```

**CentOS/RHEL:**
```bash
sudo yum install python3.11 python3-pip nodejs npm postgresql redis nginx
```

### 2. Database Setup

**PostgreSQL:**
```sql
CREATE DATABASE lms_db;
CREATE USER lms_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE lms_db TO lms_user;
```

### 3. Application Setup

1. **Create project directory:**
   ```bash
   sudo mkdir -p /var/www/lms
   cd /var/www/lms
   ```

2. **Create virtual environment:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   ```

3. **Copy your project files to the server**

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   npm install
   ```

5. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your production settings
   ```

6. **Build frontend assets:**
   ```bash
   npm run build
   ```

7. **Run Django setup:**
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser
   ```

### 4. Gunicorn Setup

Create a systemd service file `/etc/systemd/system/lms.service`:

```ini
[Unit]
Description=LMS Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/lms
Environment="PATH=/var/www/lms/venv/bin"
ExecStart=/var/www/lms/venv/bin/gunicorn -c /var/www/lms/gunicorn.conf.py lms_backend.wsgi:application
ExecReload=/bin/kill -HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable lms
sudo systemctl start lms
```

### 5. Nginx Configuration

Create `/etc/nginx/sites-available/lms`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        root /var/www/lms;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location /media/ {
        root /var/www/lms;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/lms /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. SSL Certificate (Optional but Recommended)

Using Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 7. Background Tasks Setup

Create systemd services for Celery:

`/etc/systemd/system/lms-celery.service`:
```ini
[Unit]
Description=LMS Celery Worker
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/lms
Environment="PATH=/var/www/lms/venv/bin"
ExecStart=/var/www/lms/venv/bin/celery -A lms_backend worker -l info
Restart=always

[Install]
WantedBy=multi-user.target
```

`/etc/systemd/system/lms-celery-beat.service`:
```ini
[Unit]
Description=LMS Celery Beat
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/lms
Environment="PATH=/var/www/lms/venv/bin"
ExecStart=/var/www/lms/venv/bin/celery -A lms_backend beat -l info
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable lms-celery lms-celery-beat
sudo systemctl start lms-celery lms-celery-beat
```

## Environment Variables

Key environment variables to configure:

- `SECRET_KEY`: Django secret key (generate a secure one)
- `DEBUG`: Set to `False` for production
- `ALLOWED_HOSTS`: Your domain names
- `DATABASE_*`: Database connection settings
- `GEMINI_API_KEY`: For AI-powered features
- `EMAIL_*`: Email server configuration
- `REDIS_URL`: Redis connection string

## Monitoring and Maintenance

1. **Check service status:**
   ```bash
   sudo systemctl status lms lms-celery lms-celery-beat
   ```

2. **View logs:**
   ```bash
   sudo journalctl -u lms -f
   ```

3. **Database backups:**
   ```bash
   pg_dump lms_db > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

4. **Update deployment:**
   ```bash
   git pull
   source venv/bin/activate
   pip install -r requirements.txt
   npm install && npm run build
   python manage.py migrate
   python manage.py collectstatic --noinput
   sudo systemctl restart lms lms-celery lms-celery-beat
   ```

## Security Considerations

- Keep all dependencies updated
- Use strong passwords and secure secret keys
- Enable firewall and limit access to necessary ports
- Regular security audits and updates
- Monitor logs for suspicious activity
- Use HTTPS in production
- Regular database backups

## Troubleshooting

Common issues and solutions:

1. **Static files not loading:** Check `STATIC_ROOT` and run `collectstatic`
2. **Database connection errors:** Verify database credentials and connectivity
3. **Permission denied:** Check file ownership and permissions
4. **Gunicorn won't start:** Check configuration and logs
5. **AI features not working:** Verify `GEMINI_API_KEY` is set correctly

For more help, check the logs and Django documentation.
