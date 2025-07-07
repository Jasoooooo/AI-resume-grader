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
import hashlib

# ---------- CONFIG ----------
DATABASE = 'users.db'
RESUME_DB = 'resumes.db'
SMTP_EMAIL = st.secrets["SMTP_EMAIL"]
SMTP_PASSWORD = st.secrets["SMTP_PASSWORD"]

# ---------- DATABASE SETUP ----------
def init_user_db():
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)''')
    conn.commit()
    return conn, c

def init_resume_db():
    conn = sqlite3.connect(RESUME_DB, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS resumes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, content TEXT, score REAL)''')
    conn.commit()
    return conn, c

# ---------- UTILITY FUNCTIONS ----------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def extract_keywords(text):
    words = re.findall(r'\w+', text.lower())
    return set(words + [text.lower()])  # For single and full-phrase matching

def score_resume(text, keywords):
    text = text.lower()
    matched = [kw for kw in keywords if kw.lower() in text]
    score = len(matched) / len(keywords) * 100 if keywords else 0
    return score, matched

def check_grammar(text):
    tool = language_tool_python.LanguageToolPublicAPI('en-US')
    matches = tool.check(text)
    return len(matches)

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

# ---------- STREAMLIT APP ----------
st.set_page_config(page_title="AI Resume Grader", layout="centered")

if 'login' not in st.session_state:
    st.session_state.login = False
if 'username' not in st.session_state:
    st.session_state.username = ''

st.title("Login / Signup")
auth_action = st.radio("Choose Action", ["Login", "Signup"])
username = st.text_input("Username")
password = st.text_input("Password", type="password")

conn_user, c_user = init_user_db()
conn_resume, c_resume = init_resume_db()

if st.button(auth_action):
    hashed_pw = hash_password(password)
    if auth_action == "Signup":
        c_user.execute("SELECT * FROM users WHERE username = ?", (username,))
        if c_user.fetchone():
            st.error("Username already exists!")
        else:
            c_user.execute("INSERT INTO users VALUES (?, ?)", (username, hashed_pw))
            conn_user.commit()
            st.success("Signup successful! Please login.")

    elif auth_action == "Login":
        c_user.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_pw))
        if c_user.fetchone():
            st.session_state.login = True
            st.session_state.username = username
            st.success("Login successful!")
        else:
            st.error("Incorrect username or password.")

if st.session_state.login:
    st.header("AI Resume Grader")

    job_roles = {
        "Data Scientist": [
            "python", "machine learning", "data analysis", "pandas", "numpy", "scikit-learn", "regression",
            "classification", "clustering", "data wrangling", "visualization", "tensorflow", "keras"
        ],
        "Web Developer": [
            "html", "css", "javascript", "react", "sql", "api integration", "responsive design",
            "version control", "git", "node.js", "frontend", "backend", "web security"
        ],
        "AI Engineer": [
            "deep learning", "tensorflow", "pytorch", "neural networks", "natural language processing",
            "reinforcement learning", "model deployment", "computer vision", "convolutional networks",
            "transformers", "bert", "nlp"
        ]
    }

    selected_job = st.selectbox("Select Job Role", list(job_roles.keys()))
    job_keywords = job_roles[selected_job]

    uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
    resume_text = ""

    if uploaded_file:
        if uploaded_file.size > 2 * 1024 * 1024:
            st.error("File too large. Please upload a file smaller than 2MB.")
        else:
            try:
                if uploaded_file.type == "application/pdf":
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            resume_text += text
                elif uploaded_file.type == "text/plain":
                    resume_text = uploaded_file.read().decode("utf-8")

                if not resume_text.strip():
                    st.warning("Uploaded file appears to be empty.")
                else:
                    st.markdown("### Resume Content")
                    st.text_area("", resume_text, height=400)

                    score, matched = score_resume(resume_text, job_keywords)
                    missing = [kw for kw in job_keywords if kw not in matched]

                    with st.spinner("Checking grammar..."):
                        grammar_issues = check_grammar(resume_text)

                    st.success(f"Score: {score:.2f}/100")
                    st.info(f"Matched Keywords: {', '.join(matched)}")
                    st.warning(f"Missing Keywords: {', '.join(missing)}")
                    st.error(f"Grammar Issues Found: {grammar_issues}")

                    fig, ax = plt.subplots()
                    ax.pie([len(matched), len(missing)], labels=["Matched", "Missing"],
                           autopct='%1.1f%%', colors=['green', 'red'])
                    st.pyplot(fig)
                    plt.close(fig)

                    c_resume.execute("INSERT INTO resumes (username, content, score) VALUES (?, ?, ?)",
                                     (st.session_state.username, resume_text, score))
                    conn_resume.commit()

                    pdf_file = generate_pdf(st.session_state.username, score, matched, missing, grammar_issues)
                    with open(pdf_file, "rb") as f:
                        st.download_button("Download PDF Report", f, file_name=pdf_file)

                    email = st.text_input("Enter your email to receive the report")
                    if st.button("Send Email"):
                        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
                            try:
                                send_email(email, pdf_file)
                                st.success("Report sent successfully!")
                            except Exception as e:
                                st.error(f"Failed to send email: {e}")
                        else:
                            st.warning("Invalid email format.")

                    if os.path.exists(pdf_file):
                        os.remove(pdf_file)

            except Exception as e:
                st.error(f"Something went wrong while processing the resume: {e}")

    if st.checkbox("View My Past Scores"):
        rows = c_resume.execute("SELECT score FROM resumes WHERE username = ?", (st.session_state.username,)).fetchall()
        if rows:
            scores = [r[0] for r in rows]
            st.line_chart(scores)
        else:
            st.info("No past resumes found.")
