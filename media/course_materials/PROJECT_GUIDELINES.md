# Modern AI-Powered LMS: Project Guidelines

## 1. Project Overview

### Mission
To provide a robust, scalable, and user-friendly Learning Management System (LMS) that leverages the power of AI to enhance the educational experience for students, instructors, and administrators.

### Key Features
- **Role-Based Dashboards:** Tailored experiences for Students, Instructors, and Admins.
- **AI-Powered Content Generation:** Utilizes Google Gemini to create quizzes, lesson plans, and more.
- **Comprehensive Course Management:** Create, manage, and enroll users in courses.
- **Advanced Quiz & Exam System:** Support for various question types and automated grading.
- **Assignments & Grading:** Create assignments, manage submissions, and provide feedback.
- **Interactive Discussion Forums:** Foster collaboration and communication.
- **Analytics & Reporting:** Track student progress and course effectiveness.
- **Production-Ready:** Built with a focus on security, scalability, and maintainability.

### Target Audience
- Educational Institutions (K-12, Higher Education)
- Corporate Training Programs
- Online Course Providers

---

## 2. Technical Architecture

- **Backend:** Django 5.2, Django REST Framework
- **Frontend:** Tailwind CSS
- **Database:** PostgreSQL (Production), SQLite (Development)
- **AI Integration:** Google Gemini API
- **Asynchronous Tasks:** Celery with Redis as the message broker
- **Deployment:** Docker, Gunicorn, Nginx

---

## 3. Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose

### Installation (Docker - Recommended)
1. Clone the repository.
2. Copy `.env.example` to `.env` and fill in the required values.
3. Run `docker-compose up -d --build`
4. Run database migrations: `docker-compose exec web python manage.py migrate`

### Running the Application
- **Development:** `python manage.py runserver`
- **Production:** Use the provided `gunicorn.conf.py` and `Dockerfile`.

---

## 4. User Roles & Permissions

- **Admin:** Full control over the platform, including user and course management.
- **Instructor:** Can create and manage courses, generate content, grade assignments, and view analytics.
- **Student:** Can enroll in courses, take quizzes, submit assignments, and participate in discussions.

---

## 5. Core Features Guide

### Course Management
- Instructors can create, update, and delete courses from their dashboard.
- Admins can manage all courses on the platform.

### AI Content Generation
- Instructors can use the AI tools to generate:
  - Quizzes and exams
  - Lesson plans
  - Assignment rubrics
  - Concept explanations

### Exams & Quizzes
- Multiple choice, true/false, and short answer questions are supported.
- Timed exams and automated grading for multiple-choice questions.

---

## 6. Development Workflow

### Branching Strategy
- `main`: Production-ready code.
- `develop`: Ongoing development.
- `feature/...`: For new features.

### Coding Standards
- **Formatting:** Black
- **Linting:** Flake8

### Testing
- Run tests with `pytest` or `python manage.py test`.
- Aim for high test coverage for all new features.

### CI/CD
- A GitHub Actions workflow is configured to:
  - Run tests and linting on every push.
  - Build and push a Docker image on pushes to `main`.
  - Deploy to production on pushes to `main`.

---

## 7. Deployment

Refer to `DEPLOYMENT.md` for detailed instructions on both manual and Docker-based deployment.

---

## 8. Roadmap & Future Enhancements

- **Gamification:** Badges, points, and leaderboards.
- **Mobile App:** Native iOS and Android applications.
- **Advanced Analytics:** Deeper insights into student performance.
- **Social Learning:** Peer-to-peer learning and study groups.
