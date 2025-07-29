import streamlit as st
import os
import google.generativeai as genai
from fpdf import FPDF
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Learning Path Generation Functionality
prompt = """You are a learning path generator. Given a topic, generate a structured study plan with essential resources (books, articles, courses, and videos) within 300 words.

Topic: """

def generate_learning_path(topic):
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt + topic)
    return response.text

def generate_pdf(learning_path, topic):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, txt=f"Learning Path: {topic}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, learning_path)
    pdf_output_path = "learning_path.pdf"
    pdf.output(pdf_output_path)
    return pdf_output_path

def learning_path_generator_app():
    st.subheader("📚 Learning Path Generator")
    topic = st.text_input("Enter a topic you want to study:")
    if st.button("Generate Learning Path"):
        if topic.strip():
            learning_path = generate_learning_path(topic)
            st.write(learning_path)
            st.session_state['learning_path'] = learning_path
        else:
            st.warning("Please enter a topic.")
    
    if st.button("Download Learning Path as PDF"):
        if 'learning_path' in st.session_state:
            pdf_file = generate_pdf(st.session_state['learning_path'], topic)
            with open(pdf_file, "rb") as file:
                st.download_button("Download PDF", file, file_name="learning_path.pdf")
        else:
            st.warning("Generate a learning path first.")

# Ensure the Streamlit app runs
if __name__ == "__main__":
    st.set_page_config(page_title="Learning Path Generator")
    st.title("📚 Learning Path Generator")
    learning_path_generator_app()
