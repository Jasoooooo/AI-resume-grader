import streamlit as st
import re

# Sample job description keywords
job_keywords = ["python", "machine learning", "data analysis", "sql", "communication"]

def extract_keywords(resume_text):
    words = re.findall(r'\w+', resume_text.lower())
    return set(words)

def score_resume(resume_text, job_keywords):
    resume_words = extract_keywords(resume_text)
    matched = [kw for kw in job_keywords if kw in resume_words]
    score = len(matched) / len(job_keywords) * 100
    return score, matched

st.title("📄 AI Resume Grader")
st.markdown("Upload or paste your resume below. The AI will check how well your resume matches the job description.")

resume_text = st.text_area("📋 Paste your resume text here")

if resume_text:
    score, matched = score_resume(resume_text, job_keywords)
    st.success(f"✅ Resume Score: {score:.2f}/100")
    st.markdown(f"**Matched Keywords:** {', '.join(matched)}")

    missing = [kw for kw in job_keywords if kw not in matched]
    st.warning("🔍 Missing Keywords: " + ", ".join(missing))

    if score < 50:
        st.info("⚠️ Try adding more technical or soft skills from the job description.")
    else:
        st.balloons()
        st.success("🎉 Great resume! It aligns well with the job requirements.")
