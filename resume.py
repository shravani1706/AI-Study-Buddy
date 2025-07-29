import os
import re
import spacy
import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
gemini_api_key = os.getenv("GOOGLE_API_KEY")

if not gemini_api_key:
    st.error("Gemini API key not found in .env file. Please add GEMINI_API_KEY to your .env file.")
    st.stop()

# Configure GenAI with the API key from the .env file
genai.configure(api_key=gemini_api_key)

# Ensure the spaCy model is available
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Function to extract text from a PDF file-like object
def extract_text_from_pdf_file(file_obj):
    text = ""
    reader = PdfReader(file_obj)
    for page in reader.pages:
        text += page.extract_text() + " "
    return text.strip()

# Function to clean text
def clean_text(text):
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = text.lower()
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if not token.is_stop]
    return " ".join(tokens)

# Function to rank resumes using GenAI
def rank_resumes_with_genai(job_description, uploaded_files):
    ranked_resumes = []
    model = genai.GenerativeModel("gemini-1.5-pro")
    
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith(".pdf"):
            raw_text = extract_text_from_pdf_file(uploaded_file)
            resume_text = clean_text(raw_text)
            # Construct prompt for GenAI
            prompt = (
                f"Job Description:\n{job_description}\n\n"
                f"Resume:\n{resume_text}\n\n"
                "On a scale of 1 to 10, where 10 is a perfect match, "
                "please rate the suitability of this resume for the job description. "
                "Provide only the numerical rating."
            )
            response = model.generate_content(prompt)
            # Try to extract the first float number from the response
            try:
                rating = float(response.text.strip().split()[0])
            except Exception as e:
                rating = 0.0  # Default to 0 if parsing fails
            ranked_resumes.append((uploaded_file.name, rating))
    
    # Sort resumes descending by rating
    ranked_resumes = sorted(ranked_resumes, key=lambda x: x[1], reverse=True)
    return ranked_resumes

# Function to summarize job description using GenAI
def summarize_job_description(job_description):
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(job_description)
    return response.text if hasattr(response, "text") else "No summary available."

# Streamlit UI
st.title("AI-powered Resume Screening and Ranking System")

job_desc = st.text_area("Enter Job Description")
uploaded_files = st.file_uploader("Upload Resume PDFs", type=["pdf"], accept_multiple_files=True)

if st.button("Rank Resumes"):
    if job_desc and uploaded_files:
        summary = summarize_job_description(job_desc)
        st.subheader("Job Description Summary:")
        st.write(summary)
        
        results = rank_resumes_with_genai(job_desc, uploaded_files)
        st.subheader("Ranked Resumes:")
        for rank, (filename, score) in enumerate(results, 1):
            st.write(f"{rank}. {filename} - Score: {score:.2f}")
    else:
        st.error("Please enter a valid job description and upload at least one resume PDF.")
