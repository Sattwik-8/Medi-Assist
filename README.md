# Medi-Assist 🏥

AI-powered healthcare assistant built with Flask, Machine Learning, and Gemini AI for symptom analysis, disease prediction, multilingual medical chat, and healthcare guidance.

---

## 🚀 Live Demo

🌐 Live Website: https://medi-assist-hx0e.onrender.com

---

## ✨ Features

### 🤖 AI Medical Chatbot
- Natural language symptom analysis
- General health conversation using Gemini AI
- Context-aware medical assistance
- Follow-up medical guidance

### 🧠 Machine Learning Disease Prediction
- Symptom-based disease prediction
- Trained ML model using Scikit-learn
- Confidence-aware responses
- Multiple symptom support

### 💊 Medical Guidance System
After diagnosis, users can ask:
- Medicines
- Diet suggestions
- Precautions
- Workouts / exercises
- Disease information

### 🌍 Multilingual Support
Supports:
- English
- Hindi
- Bengali

### 📄 Prescription Upload System
- Upload prescriptions/photos
- File management
- User upload history

### 🔐 Authentication System
- User login/signup
- Session management
- Protected chat routes

### 📱 Responsive UI
- Mobile-friendly interface
- Modern healthcare-themed UI
- Interactive chatbot experience

---

## 🛠️ Tech Stack

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript

### Backend
- Flask
- Python

### Machine Learning
- Scikit-learn
- Pandas
- NumPy

### AI Integration
- Gemini API

### Database
- SQLite

### Deployment
- Render
- Gunicorn

---

## 📂 Project Structure

```bash
Medi-Assist/
│
├── main.py
├── model.py
├── chat.py
├── gemini.py
├── nlp.py
├── data.py
├── safety.py
├── train_model.py
│
├── templates/
│   ├── index.html
│   ├── chat.html
│   ├── about.html
│   ├── blog.html
│   ├── developer.html
│   └── contact.html
│
├── static/
├── uploads/
├── requirements.txt
├── render.yaml
└── README.md
## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/Sattwik-8/Medi-Assist.git
cd Medi-Assist
```

---

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate virtual environment:

#### Windows
```bash
venv\Scripts\activate
```

#### Linux / Mac
```bash
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Create `.env`

Create a `.env` file in the root directory:

```env
SECRET_KEY=your_secret_key
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash-lite
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password
CONTACT_RECIPIENT=your_email@gmail.com
```

---

### 5. Run the Application

```bash
python main.py
```

Open in browser:

```text
http://127.0.0.1:5000
```

---

## 🚀 Deployment (Render)

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
gunicorn main:app --workers 2 --timeout 120 --bind 0.0.0.0:$PORT
```

---

## 🧠 Example Queries

### Symptom Prediction

```text
I have fever, headache and nausea
```

### Follow-up Questions

```text
What medicines should I take?
What should I eat?
What precautions should I take?
What exercise is safe?
Tell me more about this disease
```

### General AI Chat

```text
Explain dehydration
How to improve immunity?
What causes high blood pressure?
```

---

## 📸 Screenshots

### Homepage
(Add screenshot here)

### Chatbot Interface
(Add screenshot here)

### Mobile View
(Add screenshot here)

---

## 🔮 Future Improvements

- OCR prescription reading
- Voice assistant support
- PostgreSQL integration
- Docker deployment
- Better NLP pipeline
- AI-generated health reports
- Doctor appointment integration

---

## ⚠️ Disclaimer

This project is for educational and informational purposes only.

It is NOT a replacement for professional medical advice, diagnosis, or treatment.

Always consult a qualified healthcare professional.

---

## 👨‍💻 Developer

**Sattwik Dhara**

- GitHub: https://github.com/Sattwik-8

---

## ⭐ Support

If you found this project useful:
- Star the repository
- Share feedback
- Suggest improvements
