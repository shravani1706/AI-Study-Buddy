import streamlit as st
import json
import os
import requests
import tempfile
import re
import google.generativeai as genai
from dotenv import load_dotenv
from fpdf import FPDF

# -------------------- SETUP --------------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# -------------------- GENAI PROMPT --------------------
def generate_notes(topic, detail_level):
    """
    Generates study notes on a given topic with the specified level of detail.
    The output should be valid JSON with two keys:
      - "notes": A string containing the study notes.
      - "images": A list of valid, publicly accessible image URLs 
                  that begin with https:// and end with .jpg or .png.
    """
    prompt = f"""
    Generate study notes on the topic '{topic}' with a {detail_level} level of detail.
    The notes should include key points and explanations.
    Provide 1 to 3 valid, publicly accessible image URLs that definitely exist on the web.
    These URLs must begin with 'https://' and end with '.jpg' or '.png'.
    Ensure these links are real images that return a 200 OK response.
    Output valid JSON with exactly two keys: 'notes' (string) and 'images' (list of URLs).
    """

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text

# -------------------- OUTPUT CLEANING --------------------
def clean_ai_output(raw_output):
    """
    Removes Markdown code block formatting (triple backticks) from the raw AI output.
    """
    cleaned = raw_output.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned

def extract_json_from_text(text):
    """
    Fallback method: attempts to extract a JSON object from text by searching for
    the first '{' and the last '}' and parsing that substring.
    """
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        json_str = text[start:end+1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    return None

# -------------------- IMAGE VALIDATION --------------------
def is_valid_image_url(url, timeout=3):
    """
    Checks if the URL returns status code 200 and the content is an image.
    """
    try:
        resp = requests.head(url, timeout=timeout)
        if resp.status_code == 200:
            content_type = resp.headers.get("Content-Type", "")
            if "image" in content_type.lower():
                return True
    except Exception:
        pass
    return False

# -------------------- ENCODING FIX --------------------
def fix_encoding(text):
    """
    Replaces common smart punctuation and other Unicode characters
    with ASCII equivalents to avoid Latin-1 encoding errors in FPDF.
    """
    replacements = {
        "\u201c": '"',  # left double quote
        "\u201d": '"',  # right double quote
        "\u2018": "'",  # left single quote
        "\u2019": "'",  # right single quote
        "\u2013": "-",  # en dash
        "\u2014": "-",  # em dash
        "\u2026": "...",# ellipsis
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    # Replace or remove non-Latin-1 characters
    text = text.encode("latin-1", "replace").decode("latin-1")
    return text

# -------------------- PDF GENERATION --------------------
def fix_encoding(text):
    """
    Replaces common smart punctuation and other Unicode characters with ASCII equivalents.
    """
    replacements = {
        "\u201c": '"',
        "\u201d": '"',
        "\u2018": "'",
        "\u2019": "'",
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "..."
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    text = text.encode("latin-1", "replace").decode("latin-1")
    return text

def generate_pdf(content, image_urls=None):
    """
    Generates a PDF file containing the provided text content and images.
    Downloads each image (checking the Content-Type header to determine the file suffix)
    and embeds it in the PDF.
    
    Parameters:
      - content (str): The text content to include in the PDF.
      - image_urls (list): A list of image URLs.
    
    Returns:
      - pdf_output_path (str): The file path of the generated PDF.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, txt="AI Generated Study Notes", ln=True, align='C')
    pdf.ln(10)

    # Add text content with encoding fixes
    fixed_content = fix_encoding(content)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, fixed_content)

    # Insert images if provided
    if image_urls:
        pdf.ln(10)
        for img_url in image_urls:
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(img_url, stream=True, timeout=10, headers=headers)
                if response.ok:
                    # Determine the file suffix based on Content-Type header
                    content_type = response.headers.get("Content-Type", "").lower()
                    if "image/png" in content_type:
                        suffix = ".png"
                    elif "image/jpeg" in content_type or "image/jpg" in content_type:
                        suffix = ".jpg"
                    else:
                        suffix = ".jpg"  # default fallback

                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        for chunk in response.iter_content(chunk_size=1024):
                            tmp.write(chunk)
                        tmp_path = tmp.name

                    # Check if file is non-empty before adding
                    if os.path.getsize(tmp_path) > 0:
                        pdf.image(tmp_path, x=15, w=pdf.w - 2 * pdf.l_margin)
                    else:
                        pdf.ln(10)
                        pdf.set_font("Arial", size=12)
                        pdf.cell(200, 10, txt=f"Error: Downloaded image from {img_url} is empty.", ln=True, align='C')
                    os.remove(tmp_path)
                else:
                    pdf.ln(10)
                    pdf.set_font("Arial", size=12)
                    pdf.cell(200, 10, txt=f"Error: Received status code {response.status_code} for image URL: {img_url}", ln=True, align='C')
            except Exception as e:
                pdf.ln(10)
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt=f"Error fetching image: {str(e)}", ln=True, align='C')

    pdf_output_path = "ai_study_notes.pdf"
    pdf.output(pdf_output_path)
    return pdf_output_path
# -------------------- MAIN STREAMLIT APP --------------------
def ai_notes_generator_app():
    st.title("📝 AI-Powered Notes Generator")
    st.write("Enter a topic and select the level of detail. The AI will generate comprehensive study notes along with valid images. You can also download the generated notes as a PDF.")

    topic = st.text_input("Enter the topic:")
    detail_level = st.selectbox("Select level of detail:", ["Brief", "Moderate", "Detailed"])

    if st.button("Generate Notes") and topic:
        with st.spinner("Generating notes..."):
            raw_output = generate_notes(topic, detail_level)
            cleaned_output = clean_ai_output(raw_output)

            # Attempt JSON parsing
            try:
                result_json = json.loads(cleaned_output)
            except json.JSONDecodeError:
                result_json = extract_json_from_text(cleaned_output)
            
            if not result_json:
                st.error("Failed to parse AI output. Here is the raw output:")
                st.text(cleaned_output)
                return

            # Extract notes and images
            notes = result_json.get("notes", "No notes provided.")
            images = result_json.get("images", [])

            # Display the notes
            st.subheader("Generated Notes")
            st.markdown(notes)

            # Validate and display images
            st.subheader("Relevant Images")
            valid_images = []
            for img_url in images:
                if is_valid_image_url(img_url):
                    valid_images.append(img_url)
                    st.image(img_url, use_column_width=True)

            if not valid_images:
                st.info("No valid image URLs were provided or found.")

            # Generate the PDF
            pdf_path = generate_pdf(notes, valid_images)
            with open(pdf_path, "rb") as f:
                st.download_button("Download Notes as PDF", f, file_name="ai_study_notes.pdf")

if __name__ == "__main__":
    ai_notes_generator_app()
