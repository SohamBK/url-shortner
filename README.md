# URL Shortener - Django REST API

A full-featured URL shortening service built with Django REST Framework that enables users to convert long URLs into concise, shareable short links with comprehensive analytics and administrative oversight.

## Features

- **User Management**: Email-based authentication with OTP verification and JWT tokens
- **URL Shortening**: Generate short 6-character codes from long URLs with expiration control
- **Analytics & Tracking**: Track redirects with geolocation, device detection, and referrer data
- **Admin Panel**: System-wide dashboard for managing URLs, analytics, and users
- **Caching**: Redis-backed caching for optimized redirect performance

## Tech Stack

- **Framework**: Django 5.1 with Django REST Framework 3.15.2
- **Database**: SQLite (development); scalable to PostgreSQL/MySQL
- **Authentication**: Django REST Framework Simple JWT
- **Caching**: Redis
- **External Services**: ipinfo.io for geolocation

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd url-shortner/backend
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:

   ```bash
   python manage.py migrate
   ```

4. Start the server:
   ```bash
   python manage.py runserver
   ```

## Usage

### API Endpoints

| Module        | Endpoint                                 | Method | Purpose                    |
| ------------- | ---------------------------------------- | ------ | -------------------------- |
| **User**      | `/api/user/register/`                    | POST   | User registration with OTP |
|               | `/api/user/login/`                       | POST   | User login (returns JWT)   |
| **Shortener** | `/api/url-shortner/shorten/`             | POST   | Create shortened URL       |
|               | `/api/url-shortner/user/urls/`           | GET    | List user's URLs           |
| **Analytics** | `/api/analytics/analytic-info/<url_id>/` | GET    | Get URL access details     |
| **Redirect**  | `/<short_code>/`                         | GET    | Redirect to original URL   |

## Project Structure

```
backend/
├── users/              # Authentication & user management
├── shortner/          # URL shortening core logic
├── analytics/         # Tracking & analytics data
├── admin_panel/       # Administrative endpoints
└── url_shortner/      # Django project configuration
```
