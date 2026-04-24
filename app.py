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
# Session State
# ----------------------------
if "welcome_dismissed" not in st.session_state:
    st.session_state.welcome_dismissed = False

if "mode" not in st.session_state:
    st.session_state.mode = "exam"  # exam | review

if "incorrect_questions" not in st.session_state:
    st.session_state.incorrect_questions = []

if "questions_order" not in st.session_state:
    shuffled = copy.deepcopy(questions)
    random.shuffle(shuffled)
    st.session_state.questions_order = shuffled[:NUM_QUESTIONS]

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
# Welcome Screen
# ----------------------------
if not st.session_state.welcome_dismissed:
    st.title("💉 Welcome Vampires!! 🩸")

    st.markdown("""
This is an unofficial NHA CPT practice exam, made with questions and answers extracted directly from the NHA practice test. I, Stevie, your classmate and friend, have generously made this for you 🫵 to practice this godforsaken fucking test. It's important to note that these answers may not align with reality or anything you learned in class, but at this point we don't have much choice but to study for the test and not reality!

If you have any issues, contact:
- 📞 303-931-6977  (fastest)
- 📧 steviearmstrong@protonmail.com  
- 💬 D2L message  (slowest)

---

Legal disclaimer in case some NHA chud lawyer happens on this: this isn't made for profit so bite me and fix your exam questions before you get sued. 🤡
""")

    if st.button("Enter Quiz"):
        st.session_state.welcome_dismissed = True
        st.rerun()

    st.stop()


# ----------------------------
# Select question set
# ----------------------------
if st.session_state.mode == "exam":
    question_set = st.session_state.questions_order
else:
    question_set = st.session_state.incorrect_questions


# ----------------------------
# SAFE MODE: empty review handling
# ----------------------------
if st.session_state.mode == "review" and len(question_set) == 0:
    st.success("No missed questions — perfect score 🎉")

    if st.button("Restart Exam"):
        st.session_state.mode = "exam"
        st.session_state.index = 0
        st.session_state.score = 0
        st.session_state.incorrect_questions = []

        shuffled = copy.deepcopy(questions)
        random.shuffle(shuffled)
        st.session_state.questions_order = shuffled[:NUM_QUESTIONS]

        st.rerun()

    st.stop()


# ----------------------------
# INDEX SAFETY CHECK (FIXES CRASH)
# ----------------------------
if len(question_set) == 0:
    st.error("No questions available.")
    st.stop()

if st.session_state.index >= len(question_set):
    st.session_state.index = len(question_set) - 1


# ----------------------------
# Current question
# ----------------------------
q = question_set[st.session_state.index]

if st.session_state.shuffled_choices is None:
    choices = copy.deepcopy(q["choices"])
    random.shuffle(choices)
    st.session_state.shuffled_choices = choices


# ----------------------------
# UI
# ----------------------------
st.title("NHA CPT Practice Exam")

st.progress((st.session_state.index + 1) / len(question_set))

st.caption(f"Mode: {st.session_state.mode.upper()}")
st.caption(f"Question {st.session_state.index + 1} of {len(question_set)}")

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
    else:
        if q not in st.session_state.incorrect_questions:
            st.session_state.incorrect_questions.append(q)


for choice in st.session_state.shuffled_choices:
    if st.button(choice, key=f"{st.session_state.index}_{choice}"):
        check_answer(choice)


# ----------------------------
# Feedback
# ----------------------------
if st.session_state.attempted:
    if st.session_state.selected == q["correct_answer"]:
        st.success("Correct")
    else:
        st.error("Incorrect")
        st.write(f"Correct answer: {q['correct_answer']}")

    st.write(q["explanation"])


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
        if st.session_state.index < len(question_set) - 1:
            if st.button("Next →"):
                next_question()
                st.rerun()
        else:
            # ----------------------------
            # END SCREEN
            # ----------------------------
            st.success("Quiz complete 🎉")

            total = len(question_set)
            score = st.session_state.score
            percent = round((score / total) * 100, 2) if total else 0

            st.write(f"Score: {score} / {total}")
            st.write(f"Percentage: {percent}%")

            if len(st.session_state.incorrect_questions) > 0:
                st.write(f"Missed: {len(st.session_state.incorrect_questions)}")

            if st.button("Review Missed Questions"):
                st.session_state.mode = "review"
                st.session_state.index = 0
                st.session_state.selected = None
                st.session_state.attempted = False
                st.session_state.shuffled_choices = None
                st.rerun()

            if st.button("Restart Exam"):
                st.session_state.mode = "exam"
                st.session_state.index = 0
                st.session_state.score = 0
                st.session_state.selected = None
                st.session_state.attempted = False
                st.session_state.incorrect_questions = []
                st.session_state.shuffled_choices = None

                shuffled = copy.deepcopy(questions)
                random.shuffle(shuffled)
                st.session_state.questions_order = shuffled[:NUM_QUESTIONS]

                st.rerun()
