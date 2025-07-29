import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables and configure GenAI API
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_library_description(subject):
    """
    Generates an immersive description of "The Library of Lost Knowledge" themed
    around the chosen subject.
    """
    prompt = (
        f"Generate an immersive, mysterious description of an ancient library called "
        f"'The Library of Lost Knowledge', where every corner hides secrets related to {subject}. "
        "Describe magical artifacts, dusty tomes, and a secret passage leading to the lost manuscript."
    )
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text

def generate_challenge(subject, level):
    """
    Generates a challenge question for the given subject and level.
    The output should follow the format:
    
    Challenge: <challenge question>
    Answer: <correct answer>
    """
    prompt = (
        f"Generate a challenge question for a student in the subject {subject} at level {level} "
        "within the context of an ancient library quest. Output exactly in the following format:\n\n"
        "Challenge: <challenge question>\n"
        "Answer: <correct answer>\n"
    )
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text

def parse_challenge(challenge_text):
    """
    Parses the challenge text to extract the challenge question and the correct answer.
    """
    lines = challenge_text.split("\n")
    challenge = None
    answer = None
    for line in lines:
        line = line.strip()
        if line.lower().startswith("challenge:"):
            challenge = line[len("challenge:"):].strip()
        elif line.lower().startswith("answer:"):
            answer = line[len("answer:"):].strip().lower()
    return challenge, answer

def generate_hint(subject, challenge):
    """
    Generates a hint for the given challenge.
    """
    prompt = (
        f"Generate a helpful hint to solve the following challenge in {subject}:\n\n"
        f"Challenge: {challenge}\n\n"
        "Hint:"
    )
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)
    return response.text

def library_game():
    st.title("📚 Study Quest: The Library of Lost Knowledge")
    st.write(
        "Embark on a quest through an ancient library filled with mysteries and challenges! "
        "Your goal is to recover the legendary lost manuscript by overcoming subject-related challenges. "
        "Enter a subject you want to study and prepare to test your knowledge."
    )

    # Game Setup: Choose a subject
    subject = st.text_input("Enter a subject (e.g., Mathematics, History, Physics):")
    if st.button("Begin Your Quest") and subject:
        # Initialize session state variables
        st.session_state["subject"] = subject
        st.session_state["level"] = 1
        st.session_state["completed_levels"] = 0
        st.session_state["game_over"] = False
        st.session_state["room_description"] = generate_library_description(subject)
        challenge_text = generate_challenge(subject, st.session_state["level"])
        challenge, answer = parse_challenge(challenge_text)
        st.session_state["challenge"] = challenge
        st.session_state["correct_answer"] = answer

    if "subject" in st.session_state:
        st.subheader("The Library")
        st.write(st.session_state["room_description"])
        st.markdown("---")
        st.subheader(f"Challenge Level {st.session_state['level']}")
        st.write(st.session_state["challenge"])

        user_response = st.text_input("Enter your answer to the challenge:", key="user_response")
        if st.button("Submit Answer"):
            if user_response.strip().lower() == st.session_state["correct_answer"]:
                st.success("Correct! You've overcome this challenge.")
                st.session_state["completed_levels"] += 1
                # For this example, let's assume there are 3 levels
                if st.session_state["level"] >= 3:
                    st.balloons()
                    st.success("Congratulations! You've recovered the lost manuscript and completed your quest!")
                    st.session_state["game_over"] = True
                else:
                    st.session_state["level"] += 1
                    # Generate the next challenge for the new level
                    challenge_text = generate_challenge(st.session_state["subject"], st.session_state["level"])
                    challenge, answer = parse_challenge(challenge_text)
                    st.session_state["challenge"] = challenge
                    st.session_state["correct_answer"] = answer
                    st.experimental_rerun()
            else:
                st.error("Incorrect answer.")
                hint = generate_hint(st.session_state["subject"], st.session_state["challenge"])
                st.info(f"Hint: {hint}")

    if st.session_state.get("game_over", False):
        st.write("Thank you for playing Study Quest!")

if __name__ == "__main__":
    library_game()
