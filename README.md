# 💬 Django Chat App (DRF Based)

A simple yet powerful chat application built using Django, Django REST Framework, and token-based authentication. This app allows users to sign up, log in, send and receive messages, and filter/paginate them.

---

## 🚀 Features

- 🔐 Token-based Authentication (Login, Signup)
- 📩 Send & Receive Messages
- 🧑‍💬 Track Sender (Automatically assigns logged-in user as sender)
- 🔎 Filter messages by sender/receiver
- 📄 Pagination enabled for clean results
- ⚙️ Admin panel for managing users/messages

---

## 🛠 Tech Stack

- Backend: Django, Django REST Framework
- Database: SQLite (can be switched to PostgreSQL or others)
- Auth: DRF Token Authentication
- Deployed on render: https://mychatapp-1-ooe6.onrender.com

---

## 🚀 Live URLs

| URL | Description |
|-----|-------------|
| `/admin/` | Django Admin Panel |
| `/api/` | Base API route |
| `/api/auth/signup/` | Sign up new users |
| `/api/auth/signin/` | Login with username and password |
| `/api/chat/messages/` | Send and receive messages |
| `/messages/received/` | View received messages |
| `/api/sent-messages/` | View sent messages |
| `/messages/<int:pk>/edit/` | Edit sent messages |
| `/messages/<int:pk>/delete/` | Delete sent messages |

---

## 🧪 API Request Patterns

### 📝 Sign Up

**Endpoint:** `POST /api/auth/signup/`  
**Body:**

```json
{
  "username": "exampleusername",
  "email": "email@example.com",
  "password": "StrongPass123!",
  "password2": "StrongPass123!"
}
```

### 📝 Sign in

**Endpoint:** `POST /api/auth/signin/`  
**Body:**

```json
{
  "username": "exampleusername",
  "password": "StrongPass123!",

}
```

### 📝 Send Message

**Endpoint:** `POST /api/chat/messages/`  
**Body:**

```json
{
  "receiver": "User",
  "content": "Hello there!"
}
```

### 📝 Edit Message

**Endpoint:** `POST /messages/<int:pk>/edit/`  
**Body:**

```json
{
  "content": "Hello there!"
}
```

### 📝 delete Message

**Endpoint:** `POST /messages/<int:pk>/delete/`  
**Body:**

---

## 🔧 Setup Instructions

### 1️⃣ Clone the Repo

```bash
git clone https://github.com/Manveer101/mychatapp.git
cd mychatapp
```
