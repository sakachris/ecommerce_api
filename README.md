# E-Commerce Product Catalogue Backend

A backend API for managing an e-commerce product catalogue.  
Built with **Django REST Framework**, **PostgreSQL**, **Celery**, **RabbitMQ**, and **drf-yasg** for API documentation.  

Supports:

- Product listing, detail view, filtering, search, and pagination  
- Admin image management for products  
- Secure user registration with email verification  
- Role-based access control  
- Account deletion (with notification email)  
- Email queuing via Celery + RabbitMQ  
- Throttled resend verification endpoint  
- Swagger/OpenAPI auto-documentation  

---

## Table of Contents

1. [Features](#-features)  
2. [Tech Stack](#-tech-stack)  
3. [Prerequisites](#-prerequisites)  
4. [Installation](#-installation)  
5. [Environment Variables](#-environment-variables)  
6. [Running the Project](#-running-the-project)  
7. [Celery & RabbitMQ Setup](#-celery--rabbitmq-setup)  
8. [Database Migrations](#-database-migrations)  
9. [Admin Access](#-admin-access)  
10. [API Documentation](#-api-documentation)  
11. [Deployment Notes](#-deployment-notes)  
12. [Security Considerations](#-security-considerations)  

---

## Features

- **Product Management**
  - CRUD operations for products
  - Category assignment
  - Multiple product images with pagination
  - Search, filter, ordering
  - Admin-only access for product, category & image creation/update/delete

- **User Authentication**
  - Email-based registration
  - Email verification token system
  - Secure JWT authentication
  - Role-based permissions

- **Account Management**
  - Profile retrieval and update
  - Secure account deletion with email notification
  - Temporary admin registration endpoint (toggle via feature flag)

- **Email & Notifications**
  - Asynchronous sending via Celery + RabbitMQ
  - HTML & plaintext templates
  - Throttled resend-verification endpoint

- **Documentation**
  - Swagger UI & ReDoc via `drf-yasg`
  - Detailed endpoint descriptions and response examples

---

## Tech Stack

- **Backend Framework:** Django 5.x + Django REST Framework
- **Database:** PostgreSQL (recommended) or MySQL
- **Caching/Queue:** Redis (for token store) + RabbitMQ (for Celery tasks)
- **Task Queue:** Celery 5.x
- **API Docs:** drf-yasg (Swagger & ReDoc)
- **Authentication:** JWT (via SimpleJWT)
- **Search/Filter:** DjangoFilterBackend + DRF SearchFilter/OrderingFilter
- **Containerization:** Docker
- **MinIO:** Storage (for product images)

---

## Prerequisites

- Python 3.12+
- PostgreSQL 14+
- Redis 7+
- RabbitMQ 3.11+
- Docker
- MinIO

---

## Installation

```bash
git clone https://github.com/yourusername/ecommerce-backend.git
cd ecommerce-backend

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root directory with the following variables:

```env
SECRET_KEY=django-secret-key
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost,yourdomain

# Database configuration
DB_NAME=db_name
DB_USER=db_user
DB_PASSWORD=db_password
DB_HOST=localhost
DB_PORT=5432

# Email configuration
EMAIL_HOST=your-email-host
EMAIL_PORT=your-email-port
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email-host-user
EMAIL_HOST_PASSWORD=your-email-host-password
DEFAULT_FROM_EMAIL=your-default-from-email

CSRF_TRUSTED_ORIGINS=https://your-domain
CORS_ALLOWED_ORIGINS=https://your-domain
SESSION_COOKIE_DOMAIN=.your-domain
CSRF_COOKIE_DOMAIN=.your-domain

CREATE_SUPERUSER=true
DJANGO_SUPERUSER_USERNAME=superuser-username
DJANGO_SUPERUSER_EMAIL=superuser-email
DJANGO_SUPERUSER_FIRST_NAME=superuser-first-name
DJANGO_SUPERUSER_LAST_NAME=superuser-last-name
DJANGO_SUPERUSER_PASSWORD=superuser-password

EMAIL_VERIFICATION_TOKEN_HOURS=set-hours
PASSWORD_RESET_TOKEN_MINUTES=set-minutes

REDIS_URL=redis://localhost:6379/0
REDIS_HOST=127.0.0.1

SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT=True

# IP Geolocation API Key
IPGEOLOCATION_API_KEY=your-ip-geolocation-api

# Enable admin registration
ENABLE_ADMIN_REGISTRATION=True

# MinIO configuration
AWS_ACCESS_KEY_ID=your-id
AWS_SECRET_ACCESS_KEY=your-access-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_ENDPOINT_URL=your-endpoint-url

# Custom pagination settings
PRODUCT_PAGE_SIZE=12
CATEGORY_PAGE_SIZE=4
PRODUCT_IMAGE_PAGE_SIZE=3

```

## Running the Project

```bash
python manage.py runserver
```


---

## Celery & RabbitMQ Setup

Start RabbitMQ:

```bash
rabbitmq-server
```

Start Celery workers:

```bash
celery -A core worker -l info
```


---

## Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```


---

## Admin Access

A superuser is created when the docker image is run using the credentials provided in the env file.

Temporarily enable staff registration endpoint via .env:

ENABLE_ADMIN_REGISTRATION=True


---

## API Documentation

Swagger UI:

```bash
GET /swagger/
```

ReDoc:

```bash
GET /redoc/
```


---

## Deployment Notes

Use docker for deployment

Preferrably use Kubernetes



---

## Security Considerations

Account Deletion: Sends confirmation email after hard delete

Resend Verification Throttling: Prevents abuse via DRF throttling + custom error headers

Feature Flags: Admin registration is guarded by ENABLE_ADMIN_REGISTRATION

Role-based Permissions: Prevents unauthorized modifications

Rate Limiting: DRF throttles + Nginx-level rate limits in production



---

## License

MIT License © 2025 Chrispine 
