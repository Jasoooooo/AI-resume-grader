import streamlit as st
import re
import PyPDF2  # for PDF file reading

# --- Job keywords to match ---
job_keywords = ["python", "machine learning", "data analysis", "sql", "communication"]

# --- Function to extract keywords ---
def extract_keywords(resume_text):
    words = re.findall(r'\w+', resume_text.lower())
    return set(words)

# --- Function to score resume ---
def score_resume(resume_text, job_keywords):
    resume_words = extract_keywords(resume_text)
    matched = [kw for kw in job_keywords if kw in resume_words]
    score = len(matched) / len(job_keywords) * 100
    return score, matched

# --- UI Section ---
st.title("📄 AI Resume Grader")
st.write("Upload your resume (PDF or TXT), and get your AI-based score!")

uploaded_file = st.file_uploader("📤 Upload your resume", type=["txt", "pdf"])

resume_text = ""

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            resume_text += page.extract_text()
    elif uploaded_file.type == "text/plain":
        resume_text = uploaded_file.read().decode("utf-8")

    # Display resume content (optional)
    with st.expander("📄 View Uploaded Resume"):
        st.write(resume_text)

    # --- Grading the resume ---
    score, matched = score_resume(resume_text, job_keywords)
    st.success(f"✅ Resume Score: {score:.2f}/100")
    st.markdown(f"**Matched Keywords:** {', '.join(matched)}")

    missing = [kw for kw in job_keywords if kw not in matched]
    st.warning("🔍 Missing Keywords: " + ", ".join(missing))

    if score < 50:
        st.info("⚠️ Try adding more technical or soft skills to align with the job.")
    else:
        st.balloons()
        st.success("🎉 Strong resume! It matches well with job expectations.")

