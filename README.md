
# 🤖 AI Study Buddy

AI Study Buddy is an intelligent, all-in-one study companion designed to help learners with personalized study materials, quizzes, flashcards, video summarization, and more — all powered by AI.

---

## 🚀 Features

### 🧠 Challenge Solver
- Enter a topic and choose a question type (Theory, Technical, etc.)
- AI generates a challenge/question using Google Gemini API
- Submit your answer and track your progress

### 📄 Chat with PDFs
- Upload and interact with multiple PDFs
- Ask questions and get AI-generated responses based on the content

### 🛣️ Personalized Learning Path Generator
- Generate a customized study plan based on your input
- Download the plan for offline use

### ❓ Quiz Generator
- Create AI-generated quizzes on any topic
- Track your scores visually

### 🎥 YouTube Video Summarizer
- Paste a video link
- Get a clean, concise summary using the transcript

### 💬 Interview Prep
- Practice common and advanced interview questions

### 📝 Notes Generator
- Convert topics into neat, structured notes

### 🔖 Flashcard Generator
- Generate flashcards for active recall

### 📊 AI & Tech News Dashboard
- Stay updated with the latest AI and tech news in real time

---

## 🌟 Gamification & Progress Tracking

- 🎯 Daily Streak System
- 🏆 Badges & Leaderboard
- ✅ Solved Challenge Counter
- 🔓 Google Sign-In via Supabase
- 📊 Visual Progress Dashboard

---

## 💻 Tech Stack

### 🧩 Frontend
- HTML, CSS, JavaScript
- Interactive 3D robot (cursor-controlled)

### 🧠 Backend / AI
- Python, Streamlit
- Google Gemini API
- YouTube Transcript API
- Langchain, FAISS (for PDF chat)

### 📦 Data & Auth
- Supabase (SQL Database + Google Auth)

### 📈 Visualization
- Seaborn & Matplotlib (instead of Chart.js)

---

## 🔐 User Data

Stored securely in Supabase:
- User profile: name, email, last login
- Streaks and solved challenges
- Enrolled courses and progress

---

## 📁 Project Structure

```

/ai-study-buddy/
├── frontend/               # HTML/CSS/JS frontend
├── backend/                # Python Streamlit + AI modules
├── data/                   # Supabase integration
├── assets/                 # Icons, images, 3D robot
└── README.md

````

---

## 🧑‍💻 How to Run Locally

1. Clone the repo:
```bash
git clone https://github.com/your-username/ai-study-buddy.git
cd ai-study-buddy
````

2. Install backend dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables (API keys, Supabase URL, etc.)

4. Run the app:

```bash
streamlit run backend/app.py
```

---

## 🎯 Future Features

* Progress analytics with scoring formulas
* Study recommendations based on user history
* Real-time collaboration with friends
* AI-generated mini exams

---

## ⭐ Give a Star!

