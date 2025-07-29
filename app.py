import streamlit as st
from dotenv import load_dotenv
import os
import langchain
import langchain_community
import google.generativeai as genai
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from youtube_transcript_api import YouTubeTranscriptApi
from fpdf import FPDF
import requests
from io import BytesIO

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# PDF Generation and Chat with PDF Functionality

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
    provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
    Context:\n {context}?\n
    Question: \n{question}\n
    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()
    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)

    st.write("Reply: ", response["output_text"])

# YouTube Summarizer Functionality

prompt = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here: """

def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]
        return transcript
    except Exception as e:
        raise e

def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

def generate_pdf(content, youtube_link):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Add Title Section
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, txt="YouTube Video Summary", ln=True, align='C')

    # Add Thumbnail Image
    video_id = youtube_link.split("=")[1]
    image_url = f"http://img.youtube.com/vi/{video_id}/0.jpg"

    try:
        # Fetch the thumbnail image
        response = requests.get(image_url)
        img = BytesIO(response.content)
        pdf.image(img, x=10, y=30, w=180)  # Adjusting the image position and size
    except Exception as e:
        # If error occurs while fetching the image
        print(f"Error fetching thumbnail: {e}")
        pdf.set_font("Arial", size=12)
        pdf.ln(20)  # Space before error message
        pdf.cell(200, 10, txt="Error fetching video thumbnail.", ln=True, align='C')

    # Add Summary Content
    pdf.ln(90)  # Adding space after the image for content
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)

    # Save the PDF locally
    pdf_output_path = os.path.join(os.getcwd(), "summarized_content.pdf")
    pdf.output(pdf_output_path)

    return pdf_output_path


# Main Functionality

def main():
    st.set_page_config(page_title="Select Your Functionality")
    st.header("Choose Your Tool")

    functionality = st.radio("Choose Functionality", ("ChatPDF", "YouTube Summarizer"))

    if functionality == "ChatPDF":
        st.subheader("Chat with PDF using Gemini💁")
        user_question = st.text_input("Ask a Question from the PDF Files")

        if user_question:
            user_input(user_question)

        with st.sidebar:
            st.title("Menu:")
            pdf_docs = st.file_uploader("Upload your PDF Files", accept_multiple_files=True)
            if st.button("Submit & Process"):
                with st.spinner("Processing..."):
                    raw_text = get_pdf_text(pdf_docs)
                    text_chunks = get_text_chunks(raw_text)
                    get_vector_store(text_chunks)
                    st.success("Done")

    elif functionality == "YouTube Summarizer":
        st.subheader("YouTube Video Summarizer 💻")
        youtube_link = st.text_input("Enter YouTube Video Link:")

        if youtube_link:
            video_id = youtube_link.split("=")[1]
            st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

        if st.button("Get Detailed Notes"):
            if 'transcript_text' not in st.session_state:
                transcript_text = extract_transcript_details(youtube_link)
                st.session_state.transcript_text = transcript_text
                summary = generate_gemini_content(transcript_text, prompt)
                st.session_state.summary = summary
                st.write(summary)
            else:
                st.write(st.session_state.summary)

        user_question = st.text_input("Ask a question about the video:")

        if user_question:
            response = generate_gemini_content(st.session_state.transcript_text + "\n" + user_question, prompt)
            st.write("Answer: ", response)

        if st.button("Download Summary as PDF"):
            if 'summary' in st.session_state:
                pdf_file = generate_pdf(st.session_state.summary, youtube_link)
                st.download_button("Download PDF", pdf_file, file_name="summarized_content.pdf")

if __name__ == "__main__":
    main()
