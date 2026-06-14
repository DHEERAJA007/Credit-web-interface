# Credit-web-interface
AI-powered Credit Risk Assessment web application built with FastAPI that predicts creditworthiness, estimates default probability, and generates a credit score using Machine Learning and Scorecard modeling.
# 💳 Credit Risk Assessment System

An AI-powered Credit Risk Assessment web application built using **FastAPI** and **Machine Learning**. The system predicts whether a customer is creditworthy, estimates the probability of default, and generates a credit score based on financial and demographic information.

## 🚀 Features

- Predicts customer creditworthiness
- Calculates Probability of Default (PD)
- Generates Credit Score (300–900)
- Scorecard-based prediction using WoE Transformation
- User-friendly HTML interface
- FastAPI backend with real-time predictions
- Clean and responsive result page

---

## 🛠️ Tech Stack

- Python
- FastAPI
- Scikit-learn
- Pandas
- NumPy
- HTML
- CSS
- Jinja2 Templates
- Uvicorn

---

## 📂 Project Structure

```
Credit-Risk-Assessment/
│
├── main.py
├── credit_UI.html
├── result.html
├── model/
│   ├── trained_model.pkl
│   └── scorecard.pkl
├── static/
├── templates/
├── requirements.txt
└── README.md
```

---

## ▶️ Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/Credit-Risk-Assessment.git
```

Navigate to the project:

```bash
cd Credit-Risk-Assessment
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
uvicorn main:app --reload
```

Open your browser:

```
http://127.0.0.1:8000
```

---

## 📊 Model Output

The application provides:

- Creditworthiness Status
- Probability of Default
- Credit Score
- Risk Assessment

---

## 🎯 Use Cases

- Banking
- Financial Institutions
- Loan Approval Systems
- FinTech Applications
- Credit Risk Analysis

---


---

## 📌 Future Improvements

- Explainable AI (SHAP/LIME)
- User Authentication
- Database Integration
- Dashboard Analytics
- Model Retraining Pipeline

---

## 👨‍💻 Author

**Dheeraj Alahari**

B.Tech CSE Student | Machine Learning & Backend Development Enthusiast
