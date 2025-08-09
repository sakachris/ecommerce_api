# 🛒 E-Commerce Product Catalogue Backend

A **production-ready** backend API for managing an e-commerce product catalogue.  
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

## 📑 Table of Contents

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
11. [Testing](#-testing)  
12. [Deployment Notes](#-deployment-notes)  
13. [Security Considerations](#-security-considerations)  

---

## 🚀 Features

- **Product Management**
  - CRUD operations for products
  - Category assignment
  - Multiple product images with pagination
  - Search, filter, ordering
  - Admin-only access for product & image creation/update/delete

- **User Authentication**
  - Email-based registration
  - Email verification token system
  - Secure JWT authentication
  - Role-based permissions (`is_staff`, `is_superuser`, `guest`)

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

## 🛠 Tech Stack

- **Backend Framework:** Django 5.x + Django REST Framework
- **Database:** PostgreSQL (recommended) or MySQL
- **Caching/Queue:** Redis (for token store) + RabbitMQ (for Celery tasks)
- **Task Queue:** Celery 5.x
- **API Docs:** drf-yasg (Swagger & ReDoc)
- **Authentication:** JWT (via SimpleJWT)
- **Search/Filter:** DjangoFilterBackend + DRF SearchFilter/OrderingFilter
- **Containerization (optional):** Docker + docker-compose

---

## 📋 Prerequisites

- Python 3.12+
- PostgreSQL 14+
- Redis 7+
- RabbitMQ 3.11+
- (Optional) Docker & docker-compose

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/ecommerce-backend.git
cd ecommerce-backend

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt

---

## 5. ⚙ Environment Variables

Create a `.env` file in the project root directory with the following variables:

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,localhost,127.0.0.1

DATABASE_URL=postgres://user:password@localhost:5432/ecommerce_db

REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=redis://localhost:6379/1

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yourmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=no-reply@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=no-reply@yourdomain.com

PUBLIC_BASE_URL=https://yourdomain.com
ENABLE_ADMIN_REGISTRATION=True

## Running the Project

```bash
python manage.py runserver


---

## 📬 Celery & RabbitMQ Setup

Start RabbitMQ:

```bash
rabbitmq-server

Start Celery workers:

```bash
celery -A core worker -l info


---

## 🗄 Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate


---

## 👑 Admin Access

A superuser is created when the docker image is run using the credentials provided in the env file.

Temporarily enable staff registration endpoint via .env:

ENABLE_ADMIN_REGISTRATION=True


---

## 📖 API Documentation

Swagger UI:

GET /swagger/

ReDoc:

GET /redoc/


---

🚀 Deployment Notes

Use Gunicorn or uWSGI behind Nginx for production

Set DEBUG=False and configure ALLOWED_HOSTS

Use HTTPS (Let’s Encrypt or managed SSL)

Configure PostgreSQL connection pooling (e.g., pgbouncer)

Use persistent volumes for RabbitMQ & Redis in Docker

Rotate SECRET_KEY and credentials regularly



---

🔐 Security Considerations

Account Deletion: Sends confirmation email after hard delete

Resend Verification Throttling: Prevents abuse via DRF throttling + custom error headers

Feature Flags: Admin registration is guarded by ENABLE_ADMIN_REGISTRATION

Role-based Permissions: Prevents unauthorized modifications

Rate Limiting: DRF throttles + Nginx-level rate limits in production



---

📜 License

MIT License © 2025 Your Name
# E-commerce Product Catalogue API
