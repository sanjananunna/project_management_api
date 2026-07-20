# Project Management API

A backend REST API built using **FastAPI**, **SQLAlchemy**, **SQLite**, and **JWT Authentication** for managing projects, users, and tasks with **Role-Based Access Control (RBAC)**.

---

## Features

### Authentication
- User Signup
- User Login
- JWT Token Authentication
- Protected Routes

### Role-Based Access Control (RBAC)
- Admin
- Manager
- Member

### Project Management
- Create Project
- View All Projects
- View Project by ID
- Delete Project

### Project Members
- Add Members to a Project
- View Project Members

### Task Management
- Create Task
- View All Tasks
- View Task by ID
- Update Task
- Delete Task

---

## Technologies Used

- Python 3
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Passlib (bcrypt)
- Python-JOSE (JWT)
- Uvicorn

---

## Project Structure

```
project_management_api/
│
├── app/
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── projects.py
│   │   ├── members.py
│   │   └── tasks.py
│   │
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── oauth2.py
│   ├── permissions.py
│   ├── security.py
│   └── main.py
│
├── requirements.txt
├── README.md
└── project_management.db
```

---

## Installation

### Clone the repository

```bash
git clone https://github.com/your-username/project_management_api.git
```

### Navigate to the project folder

```bash
cd project_management_api
```

### Create a virtual environment

```bash
python -m venv .venv
```

### Activate the virtual environment

**Windows**

```bash
.venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run the Application

```bash
python -m uvicorn app.main:app --reload
```

Server:

```
http://127.0.0.1:8000
```

Swagger Documentation:

```
http://127.0.0.1:8000/docs
```

---

## Authentication

Use the following endpoints:

### Signup

```
POST /auth/signup
```

### Login

```
POST /auth/login
```

### Current User

```
GET /auth/me
```

---

## Project APIs

```
POST   /projects
GET    /projects
GET    /projects/{project_id}
DELETE /projects/{project_id}
```

---

## Project Member APIs

```
POST /members
GET  /members/{project_id}
```

---

## Task APIs

```
POST   /tasks
GET    /tasks
GET    /tasks/{task_id}
PUT    /tasks/{task_id}
DELETE /tasks/{task_id}
```

---

## Roles

### Admin
- Create projects
- Delete projects
- Add project members
- Create tasks
- Update tasks
- Delete tasks

### Manager
- View projects
- Create tasks
- Update tasks

### Member
- View projects
- View tasks
- Update only assigned tasks

---

## API Testing

The API can be tested using:

- Swagger UI (`/docs`)
- Postman

---

## Author

**Sanjana Nunna**

Backend Developer Project using FastAPI