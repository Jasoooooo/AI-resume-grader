import streamlit as st
import re
import sqlite3
import PyPDF2
import language_tool_python
import matplotlib.pyplot as plt
from fpdf import FPDF
import os
import smtplib
from email.message import EmailMessage

# ---------- CONFIG ----------
DATABASE = 'users.db'
RESUME_DB = 'resumes.db'
SMTP_EMAIL = 'your_email@gmail.com'   # Replace with your Gmail
SMTP_PASSWORD = 'your_app_password'   # Replace with App Password or email password

# ---------- INITIAL SETUP ----------
conn_user = sqlite3.connect(DATABASE)
c_user = conn_user.cursor()
c_user.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)''')
conn_user.commit()

conn_resume = sqlite3.connect(RESUME_DB, check_same_thread=False)
c_resume = conn_resume.cursor()
c_resume.execute('''CREATE TABLE IF NOT EXISTS resumes
             (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT, score REAL)''')
conn_resume.commit()

# ---------- FUNCTIONS ----------
def extract_keywords(text):
    return set(re.findall(r'\w+', text.lower()))

def score_resume(text, keywords):
    words = extract_keywords(text)
    matched = [kw for kw in keywords if kw in words]
    score = len(matched) / len(keywords) * 100
    return score, matched

def check_grammar(text):
    tool = language_tool_python.LanguageTool('en-US')
    return len(tool.check(text))

def generate_pdf(username, score, matched, missing, grammar_issues):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="AI Resume Feedback Report", ln=True, align='C')
    pdf.ln(10)
    pdf.multi_cell(0, 10, f"User: {username}\n\nScore: {score:.2f}/100\n\nMatched Keywords: {', '.join(matched)}\n\nMissing Keywords: {', '.join(missing)}\n\nGrammar Issues: {grammar_issues}")
    file_path = f"{username}_report.pdf"
    pdf.output(file_path)
    return file_path

def send_email(to_email, file_path):
    msg = EmailMessage()
    msg['Subject'] = 'Your Resume Grader Report'
    msg['From'] = SMTP_EMAIL
    msg['To'] = to_email
    msg.set_content('Find attached your AI Resume Feedback Report.')

    with open(file_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=os.path.basename(file_path))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SMTP_EMAIL, SMTP_PASSWORD)
        smtp.send_message(msg)

# ---------- APP ----------
st.set_page_config(page_title="AI Resume Grader", layout="centered")

# Theme toggle
theme = st.selectbox("Choose Theme", ["Light", "Dark"])
if theme == "Dark":
    st.markdown("""
        <style>
            body {background-color: #111; color: white;}
        </style>
    """, unsafe_allow_html=True)

st.title("🔐 Login / Signup")
auth_action = st.radio("Choose Action", ["Login", "Signup"])
username = st.text_input("Username")
password = st.text_input("Password", type="password")

login_success = False

if st.button(auth_action):
    if auth_action == "Signup":
        c_user.execute("SELECT * FROM users WHERE username = ?", (username,))
        if c_user.fetchone():
            st.error("Username already exists!")
        else:
            c_user.execute("INSERT INTO users VALUES (?, ?)", (username, password))
            conn_user.commit()
            st.success("Signup successful! Please login.")

    elif auth_action == "Login":
        c_user.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        if c_user.fetchone():
            st.success("Login successful!")
            login_success = True
        else:
            st.error("Incorrect username or password.")

# Resume Grader UI
if login_success:
    st.title("📄 AI Resume Grader")

    job_roles = {
        "Data Scientist": ["python", "machine learning", "data analysis", "pandas", "numpy"],
        "Web Developer": ["html", "css", "javascript", "react", "sql"],
        "AI Engineer": ["deep learning", "tensorflow", "pytorch", "neural networks", "nlp"]
    }

    selected_job = st.selectbox("🎯 Select Job Role", list(job_roles.keys()))
    job_keywords = job_roles[selected_job]

    uploaded_file = st.file_uploader("📤 Upload your resume (PDF/TXT)", type=["pdf", "txt"])
    resume_text = ""

    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                resume_text += page.extract_text()
        elif uploaded_file.type == "text/plain":
            resume_text = uploaded_file.read().decode("utf-8")

        st.markdown("### 📄 Resume Content")
        st.text_area("", resume_text, height=400)

        score, matched = score_resume(resume_text, job_keywords)
        missing = [kw for kw in job_keywords if kw not in matched]
        grammar_issues = check_grammar(resume_text)

        st.success(f"✅ Resume Score: {score:.2f}/100")
        st.info(f"🧠 Matched Keywords: {', '.join(matched)}")
        st.warning(f"🚫 Missing Keywords: {', '.join(missing)}")
        st.error(f"📝 Grammar Issues Found: {grammar_issues}")

        # Pie Chart
        st.markdown("### 📊 Skill Match Visualization")
        fig, ax = plt.subplots()
        ax.pie([len(matched), len(missing)], labels=["Matched", "Missing"], autopct='%1.1f%%', colors=['green', 'red'])
        st.pyplot(fig)

        # Save to DB
        c_resume.execute("INSERT INTO resumes (username, content, score) VALUES (?, ?, ?)",
                         (username, resume_text, score))
        conn_resume.commit()

        # PDF Generation + Download
        pdf_file = generate_pdf(username, score, matched, missing, grammar_issues)
        with open(pdf_file, "rb") as f:
            st.download_button("📥 Download PDF Report", f, file_name=pdf_file)

        # Email Report
        email = st.text_input("📧 Enter your email to receive the report")
        if st.button("📤 Send Email"):
            if email:
                try:
                    send_email(email, pdf_file)
                    st.success("📧 Report sent successfully!")
                except Exception as e:
                    st.error(f"Failed to send email: {e}")
            else:
                st.warning("Please enter a valid email.")

        os.remove(pdf_file)

    if st.checkbox("📂 View My Past Scores"):
        rows = c_resume.execute("SELECT score FROM resumes WHERE username = ?", (username,)).fetchall()
        if rows:
            scores = [r[0] for r in rows]
            st.line_chart(scores)
        else:
            st.info("No past resumes found.")
