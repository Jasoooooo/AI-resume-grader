# AI Resume Grader

An interactive web app built using Python, Streamlit, and SQLite that helps users analyze and improve their resumes using AI techniques. It scores resumes based on keyword match, grammar quality, and generates a personalized PDF report.

---

## Live App
[Click here to try the app](https://ai-resume-grader.streamlit.app) *(replace this with your actual Streamlit Cloud link)*

---

## Features

- User login and signup system (SQLite-based)
- Upload resume as PDF or TXT file
- Analyze resume against job-specific keywords
- Check for grammar issues using LanguageTool
- Visualize results using pie chart
- Generate personalized PDF report
- Option to email the report
- Light/Dark mode UI toggle
- Resume history tracker (line chart)

---

## How It Works

1. Sign up or log in
2. Upload your resume file (PDF or TXT)
3. Select your desired job role
4. The app:
   - Extracts text
   - Scores based on keyword match
   - Checks grammar
   - Stores the result in database
5. Shows a pie chart of matched vs missing keywords
6. Allows PDF report download or email
7. Tracks your historical scores

---

## Tech Stack

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-red)
![SQLite](https://img.shields.io/badge/SQLite-DB-lightgrey)
![PyPDF2](https://img.shields.io/badge/PDF--Parser-green)
![FPDF](https://img.shields.io/badge/Report--PDF-lightblue)
![LanguageTool](https://img.shields.io/badge/Grammar--Check-orange)

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/ai-resume-grader.git
cd ai-resume-grader
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app locally
```bash
streamlit run app.py
```

Note: The `users.db` and `resumes.db` databases are created automatically on first run.

---

## Screenshots

### Login Page
![Login Screenshot](screenshots/login.png)

### Resume Upload and Score
![Resume Analysis](screenshots/analysis.png)

### Skill Match Chart
![Pie Chart](screenshots/chart.png)

You can add these screenshots manually under a `screenshots/` folder.

---

## Email Configuration (Optional)

If you want to enable PDF email sending:
1. Enable "Less secure apps" or use Gmail App Password
2. Set your credentials in `app.py`:
```python
SMTP_EMAIL = 'your_email@gmail.com'
SMTP_PASSWORD = 'your_app_password'
```

---

## Acknowledgements
- Streamlit (https://streamlit.io/)
- LanguageTool (https://languagetool.org/)
- FPDF (https://pyfpdf.github.io/)
- PyPDF2 (https://pypi.org/project/PyPDF2/)

---

## License
This project is open source and available under the MIT License.
