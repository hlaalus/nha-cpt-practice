import streamlit as st
import json
import random
import copy

# ----------------------------
# Settings
# ----------------------------
NUM_QUESTIONS = 50

# ----------------------------
# Load questions
# ----------------------------
with open("questions.json", "r") as f:
    raw_questions = json.load(f)

# ----------------------------
# Normalize questions
# ----------------------------
def normalize_questions(data):
    cleaned = []

    for q in data:
        question_text = q.get("question", "")

        # Remove accidental numbering like "12. Question text"
        if ". " in question_text[:10]:
            try:
                question_text = question_text.split(". ", 1)[1]
            except:
                pass

        correct = q.get("correct_answer")
        choices = q.get("choices", [])

        if isinstance(correct, int):
            correct_answer = choices[correct]
        else:
            correct_answer = correct

        cleaned.append({
            "id": q.get("id"),
            "question": question_text,
            "choices": choices,
            "correct_answer": correct_answer,
            "explanation": q.get("explanation", "")
        })

    return cleaned


questions = normalize_questions(raw_questions)

# ----------------------------
# Welcome screen state
# ----------------------------
if "welcome_dismissed" not in st.session_state:
    st.session_state.welcome_dismissed = False

# ----------------------------
# Pick 50 random questions ONCE per session
# ----------------------------
if "questions_order" not in st.session_state:
    shuffled = copy.deepcopy(questions)
    random.shuffle(shuffled)
    st.session_state.questions_order = shuffled[:NUM_QUESTIONS]

# ----------------------------
# Session state init
# ----------------------------
if "index" not in st.session_state:
    st.session_state.index = 0

if "selected" not in st.session_state:
    st.session_state.selected = None

if "attempted" not in st.session_state:
    st.session_state.attempted = False

if "score" not in st.session_state:
    st.session_state.score = 0

if "shuffled_choices" not in st.session_state:
    st.session_state.shuffled_choices = None


# ----------------------------
# WELCOME SCREEN
# ----------------------------
if not st.session_state.welcome_dismissed:
    st.title("💉 Welcome vampires! 🩸")

    st.markdown("""
This is an unofficial NHA CPT practice exam.
You will receive 50 random questions per session.

Good luck.
""")

    if st.button("Enter Quiz"):
        st.session_state.welcome_dismissed = True
        st.rerun()

    st.stop()


# ----------------------------
# Current question
# ----------------------------
q = st.session_state.questions_order[st.session_state.index]

if st.session_state.shuffled_choices is None:
    choices = copy.deepcopy(q["choices"])
    random.shuffle(choices)
    st.session_state.shuffled_choices = choices


# ----------------------------
# UI
# ----------------------------
st.title("NHA CPT Practice Exam")

st.progress((st.session_state.index + 1) / len(st.session_state.questions_order))

st.caption(f"Question {st.session_state.index + 1} of {len(st.session_state.questions_order)}")
st.caption(f"Score: {st.session_state.score}")

st.markdown("---")

st.subheader(q["question"])


# ----------------------------
# Answer logic
# ----------------------------
def check_answer(choice):
    st.session_state.selected = choice
    st.session_state.attempted = True

    if choice == q["correct_answer"]:
        st.session_state.score += 1


for choice in st.session_state.shuffled_choices:
    if st.button(choice, key=f"{st.session_state.index}_{choice}"):
        check_answer(choice)


# ----------------------------
# Feedback
# ----------------------------
if st.session_state.attempted and st.session_state.selected:
    if st.session_state.selected == q["correct_answer"]:
        st.success("Correct")
        st.markdown(f"**Explanation:** {q['explanation']}")
    else:
        st.error("Incorrect")
        st.markdown(f"**Correct answer:** {q['correct_answer']}")
        st.markdown(f"**Explanation:** {q['explanation']}")


st.markdown("<br><br>", unsafe_allow_html=True)


# ----------------------------
# Navigation
# ----------------------------
def next_question():
    st.session_state.index += 1
    st.session_state.selected = None
    st.session_state.attempted = False
    st.session_state.shuffled_choices = None


col1, col2 = st.columns(2)

with col1:
    if st.button("Skip ⏭"):
        next_question()
        st.rerun()

with col2:
    if st.session_state.attempted:
        if st.session_state.index < len(st.session_state.questions_order) - 1:
            if st.button("Next →"):
                next_question()
                st.rerun()
        else:
            st.success("Quiz complete 🎉")
            st.write(f"Final Score: {st.session_state.score} / {len(st.session_state.questions_order)}")

            if st.button("Restart"):
                st.session_state.index = 0
                st.session_state.score = 0
                st.session_state.selected = None
                st.session_state.attempted = False
                st.session_state.shuffled_choices = None

                shuffled = copy.deepcopy(questions)
                random.shuffle(shuffled)
                st.session_state.questions_order = shuffled[:NUM_QUESTIONS]

                st.rerun()
