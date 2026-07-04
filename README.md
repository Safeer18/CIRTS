# 🛡️ CIRTS - Cybercrime Incident Reporting & Tracking System

A secure, full-stack **Cybercrime Incident Reporting & Tracking System (CIRTS)** built to streamline the reporting, investigation, and management of cybercrime cases. The platform provides separate user and administrator interfaces, secure authentication, and efficient case tracking for improved incident response.

---

## 🚀 Overview

CIRTS enables users to report cybercrime incidents through an intuitive web interface while providing administrators with tools to review, assign, update, and manage cases securely.

The system is designed to demonstrate practical implementation of secure authentication, database management, role-based access control, and web application development using Python and Flask.

---

## ✨ Features

### 👤 User Module

- Secure User Registration & Login
- File Cybercrime Complaints
- Upload Supporting Evidence
- View Complaint Status
- Track Investigation Progress
- Update User Profile

### 👨‍💼 Admin Module

- Secure Administrator Login
- Dashboard with Case Statistics
- View All Reported Incidents
- Update Complaint Status
- Manage Registered Users
- Review Uploaded Evidence

### 🔒 Security Features

- Password Hashing
- Secure Authentication
- Session Management
- Role-Based Access Control
- Input Validation
- SQL Injection Prevention

---

# 🛠 Tech Stack

### Frontend

- HTML5
- CSS3
- Bootstrap
- JavaScript

### Backend

- Python
- Flask
- Jinja2

### Database

- MySQL

### Tools

- Flask
- Flask SQLAlchemy
- Flask-WTF
- Werkzeug
- Git
- GitHub

---

# 📂 Project Structure

```text
CIRTS/
│
├── app.py
├── config.py
├── requirements.txt
├── templates/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── models/
├── routes/
├── database/
├── uploads/
└── README.md
```

---

# ⚙ Installation

## Clone Repository

```bash
git clone https://github.com/Safeer18/CIRTS.git
```

Move into the project directory

```bash
cd CIRTS
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Configure your database.

Run the Flask application.

```bash
python app.py
```

Visit

```
http://localhost:5000
```

---

# 📊 Database

The project uses **MySQL** for secure storage of:

- User Accounts
- Complaint Records
- Case Status
- Uploaded Evidence
- Administrator Accounts

---

# 🔐 Security Highlights

- Password Hashing
- Session Authentication
- Protected Routes
- Secure File Upload Handling
- Input Validation
- Role-Based Authorization

---

# 🎯 Learning Objectives

This project demonstrates practical implementation of:

- Full Stack Web Development
- Cybercrime Case Management
- Secure Authentication
- Database Design
- RESTful Application Development
- Cybersecurity Best Practices

---

# 👨‍💻 Author

**Safeer Husain Zaidi**

B.Tech Computer Science & Engineering (Cyber Security)

Graphic Era Deemed to be University

GitHub: https://github.com/Safeer18

---

## ⭐ Support

If you found this project useful, consider giving it a **⭐ Star** on GitHub.
