import streamlit as st
import os
import google.generativeai as genai
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from fpdf import FPDF

# Load environment variables and configure GenAI
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_text_from_pdf(pdf_file):
    """
    Extracts text from all pages of an uploaded PDF.
    """
    text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()

def generate_flashcards(notes_text, num_flashcards=10):
    """
    Uses GenAI to generate flashcards (in Q&A format) based on the provided study notes.
    The prompt instructs the model to output the flashcards in the following format:
    
    Flashcard 1:
    Q: <question>
    A: <answer>
    
    Flashcard 2:
    Q: <question>
    A: <answer>
    
    ...
    """
    prompt = (
        "You are a helpful study assistant. Based on the following study notes, generate flashcards "
        "in a Q&A format. Each flashcard should have a question and a concise answer. Format the output as follows:\n\n"
        "Flashcard 1:\n"
        "Q: <question>\n"
        "A: <answer>\n\n"
        "Flashcard 2:\n"
        "Q: <question>\n"
        "A: <answer>\n\n"
        "Please generate {} flashcards.\n\n"
        "Study Notes:\n{}".format(num_flashcards, notes_text)
    )
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text

def generate_pdf_from_flashcards(content):
    """
    Generates a PDF file containing the flashcards.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, txt="Generated Flashcards", ln=True, align='C')
    pdf.ln(10)

    # Content
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)

    pdf_output_path = "flashcards.pdf"
    pdf.output(pdf_output_path)
    return pdf_output_path

def flashcard_generator_app():
    st.title("📚 Flashcard Generator")
    st.write("Upload your study notes (in PDF format) and generate flashcards to enhance your learning!")

    uploaded_pdf = st.file_uploader("Upload a PDF", type=["pdf"])
    num_flashcards = st.number_input("Number of flashcards to generate", min_value=1, max_value=50, value=10)

    if uploaded_pdf:
        with st.spinner("Extracting text from PDF..."):
            notes_text = extract_text_from_pdf(uploaded_pdf)
        
        if notes_text:
            if st.button("Generate Flashcards"):
                with st.spinner("Generating flashcards..."):
                    flashcards = generate_flashcards(notes_text, num_flashcards)
                    st.subheader("Generated Flashcards")
                    st.text_area("Flashcards", flashcards, height=400)
                    
                    # Generate PDF for download
                    pdf_path = generate_pdf_from_flashcards(flashcards)
                    with open(pdf_path, "rb") as f:
                        st.download_button("Download Flashcards as PDF", f, file_name="flashcards.pdf")
        else:
            st.error("No text could be extracted from the uploaded PDF.")

if __name__ == "__main__":
    flashcard_generator_app()
