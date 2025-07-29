import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables and configure the API
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_interview_questions(role, interview_type, num_questions):
    """
    Uses GenAI to generate a list of interview questions for a given role and interview type.
    The questions are returned as a list of strings.
    """
    prompt = (
        f"Generate {num_questions} challenging interview questions for a candidate applying for a {role} role "
        f"for a {interview_type} interview. List one question per line."
    )
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    # Split the output into lines and filter out empty lines.
    questions = [line.strip() for line in response.text.split("\n") if line.strip()]
    return questions

def review_answer(question, answer):
    """
    Uses GenAI to review the provided answer.
    The review includes strengths, weaknesses, and suggestions for improvement.
    """
    prompt = (
        f"Review the following interview answer. Provide detailed feedback, "
        f"including strengths, weaknesses, and suggestions for improvement.\n\n"
        f"Question: {question}\n"
        f"Answer: {answer}\n\n"
        "Feedback:"
    )
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text

def interview_prep_app():
    st.title("🚀 Interview Preparation Assistant")
    st.write("Prepare for your upcoming interview with AI-generated questions and personalized feedback!")

    # Interview setup inputs
    role = st.text_input("Enter the job role you are applying for (e.g., Software Engineer, Data Scientist):")
    interview_type = st.selectbox("Select interview type:", ["Technical", "HR", "Behavioral", "Case Study"])
    num_questions = st.number_input("How many interview questions would you like to practice?", 
                                    min_value=1, max_value=20, value=5)

    # Generate interview questions when button is pressed
    if st.button("Generate Interview Questions") and role:
        questions = generate_interview_questions(role, interview_type, num_questions)
        st.session_state["interview_questions"] = questions
        st.session_state["current_question_index"] = 0
        st.session_state["user_answers"] = {}
        st.session_state["feedback"] = {}

    # If questions have been generated, show the current question
    if "interview_questions" in st.session_state:
        questions = st.session_state["interview_questions"]
        idx = st.session_state.get("current_question_index", 0)
        if idx < len(questions):
            st.subheader(f"Question {idx + 1} of {len(questions)}")
            current_question = questions[idx]
            st.write(current_question)
            # Each text area uses a key based on the current question index.
            user_answer = st.text_area("Your Answer:", key=f"answer_{idx}")
            
            if st.button("Submit Answer", key=f"submit_{idx}"):
                # Save the user's answer and generate feedback
                st.session_state["user_answers"][idx] = user_answer
                feedback = review_answer(current_question, user_answer)
                st.session_state["feedback"][idx] = feedback
                st.success("Feedback generated below:")
                st.write(feedback)
            
            # Provide a "Next Question" button if an answer has been submitted
            if st.session_state["user_answers"].get(idx):
                if st.button("Next Question", key=f"next_{idx}"):
                    st.session_state["current_question_index"] = idx + 1
                    # When the index updates, a new text area with a new key is rendered.
        else:
            st.success("You've completed all the interview questions! Review your answers and feedback below.")
            for i, q in enumerate(questions):
                st.markdown(f"**Q{i+1}: {q}**")
                answer = st.session_state["user_answers"].get(i, "No answer provided")
                feedback = st.session_state["feedback"].get(i, "No feedback available")
                st.write(f"**Your Answer:** {answer}")
                st.write(f"**Feedback:** {feedback}")
            if st.button("Reset Practice"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]

if __name__ == "__main__":
    interview_prep_app()
