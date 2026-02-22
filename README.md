# 🎓 PersonalizedU  
## 🚀 AI-Powered Personalized Learning Assistant

> Transforming generic online learning into adaptive, intelligent, and conversational education.

---

# 🏆 Problem Statement

Traditional online learning platforms are:

- ❌ One-size-fits-all  
- ❌ Overwhelming with irrelevant content  
- ❌ Not adaptive to user progress  
- ❌ Lacking conversational guidance  

Learners often struggle to find the *right* resources tailored to their skills, goals, and pace.

---

# 💡 Solution

**PersonalizedU** is an AI-powered learning assistant that:

✅ Understands users through conversation  
✅ Assesses skill levels dynamically  
✅ Recommends personalized learning paths  
✅ Tracks real-time progress  
✅ Adapts recommendations over time  

All through a chatbot-driven interface.

---

# 🧠 How It Works
User (Frontend UI)
↓
Dialogflow (NLP Intent Detection)
↓
Node.js Webhook (Intent Router)
↓
Django REST API (Business Logic + AI Engine)
↓
Database (Profiles, Courses, Assessments)

---

# ✨ Key Features

## 🤖 Conversational AI Assistant
- Powered by Dialogflow
- Detects learning goals & user intent
- Provides intelligent responses

## 📝 Skill Assessment Engine
- Dynamic quiz system
- JSON-based question structure
- Automated scoring
- Stores assessment history

## 🎯 Personalized Recommendations
- Filters by experience level
- Matches interests & goals
- Excludes completed courses
- Ranks by rating

## 📊 Progress Tracking
- Tracks completion percentage
- Logs course interactions
- Updates learning paths

## 🎨 Modern UI
- Animated responsive design
- Pink/Blue theme switching
- Voice interaction support

---

# 🛠 Tech Stack

### Frontend
- HTML5
- CSS3 (Animated UI)
- JavaScript
- Web Speech API

### Backend
- Python 3.11
- Django
- Django REST Framework
- JWT Authentication (SimpleJWT)

### Webhook
- Node.js
- Express.js
- Axios

### NLP
- Google Dialogflow

### Database
- SQLite (Dev)
- PostgreSQL (Production Ready)

---

# 🔐 Authentication Flow

1️⃣ Login  
POST /api/auth/login/

2️⃣ Receive JWT Token  

3️⃣ Secure API Access  
Authorization: Bearer <token>

Protected endpoints:
- Profile
- Recommendations
- Progress
- Assessment submission

---

# 📂 Project Structure
U-Project/
│
├── backend/
│   ├── __pycache__/
│   ├── learning/
│   │   ├── __pycache__/
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   ├── views.py
│   │
│   ├── __init__.py
│   ├── asgi.py
│   ├── manage.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│
├── dialogflow-webhook/
│   ├── node_modules/
│   ├── index.js
│   ├── package.json

---

# 🔄 Demo Flow

### Scenario: User wants to learn Python

1. User says: *"I want to learn Python"*
2. Dialogflow detects → `set-goal`
3. Webhook calls Django API
4. Profile updates
5. Recommendation engine filters courses
6. Personalized courses displayed

---

# ⚙️ How To Run Locally

## 1️⃣ Backend
python -m venv env
env\Scripts\activate
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers
cd backend
python manage.py migrate
python manage.py runserver

Backend:  
`http://127.0.0.1:8000/`

---

## 2️⃣ Webhook
cd dialogflow-webhook
npm install
node index.js

Webhook:  
`http://localhost:3000/`

---

## 3️⃣ Dialogflow

Set Fulfillment URL to:http://localhost:3000/webhook

Enable webhook for all custom intents.

---

## 4️⃣ Frontend

Open:main.html

---

# 🚀 Future Enhancements

- 🔥 ML-based recommendation (TF-IDF / SVD)
- 📈 Adaptive learning path optimization
- ☁ Cloud deployment (GCP / AWS)
- 🐳 Docker containerization
- 📊 Analytics dashboard
- 📱 Mobile responsive PWA version

---

# 🏁 Value Proposition

✔ Combines NLP + Backend AI logic  
✔ Real-world scalable architecture  
✔ Secure authentication system  
✔ Modular microservice-ready design  
✔ Expandable to ML-driven personalization  

This is not just a chatbot — it’s an adaptive AI learning ecosystem.

---

# 👩‍💻 Team

**Ruchika Verma**  
AI & Machine Learning Enthusiast  
Full-Stack Developer  

---

# 📌 Status

✅ Dialogflow Integration  
✅ Django Backend API  
✅ JWT Authentication  
✅ Recommendation Engine  
✅ Assessment System  
✅ Progress Tracking  
🚀 Deployment Ready



