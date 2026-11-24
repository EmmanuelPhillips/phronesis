import time
from uuid import uuid4

import streamlit as st

from phronesis.models import Attempt
from phronesis.repository import (
    create_learner,
    get_learner,
    get_all_tasks,
    record_attempt,
    get_learner_attempts,
)
from phronesis.seed import seed_database


# --------------------------------------------------
# Application configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Phronesis",
    page_icon="🧠",
    layout="wide",
)

st.title("Phronesis")
st.caption("Adaptive programming practice for better code comprehension.")


# --------------------------------------------------
# Initialise application data
# --------------------------------------------------

seed_database()

LEARNER_ID = "local-learner"

learner = get_learner(LEARNER_ID)

if learner is None:
    learner = create_learner(
        name="Local Learner",
        learner_id=LEARNER_ID,
    )


# --------------------------------------------------
# Load available exercises
# --------------------------------------------------

tasks = get_all_tasks()

if not tasks:
    st.error("No exercises are currently available.")
    st.stop()


# --------------------------------------------------
# Session state
# --------------------------------------------------

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

if "hints_used" not in st.session_state:
    st.session_state.hints_used = 0

if "hint_index" not in st.session_state:
    st.session_state.hint_index = 0

if "submitted_task_id" not in st.session_state:
    st.session_state.submitted_task_id = None

if "last_result" not in st.session_state:
    st.session_state.last_result = None


# --------------------------------------------------
# Exercise selection
# --------------------------------------------------

task_options = {
    task.title: task
    for task in tasks
}

selected_title = st.selectbox(
    "Choose an exercise",
    options=list(task_options.keys()),
)

task = task_options[selected_title]


# Reset exercise-specific state when changing tasks
if st.session_state.get("current_task_id") != task.id:
    st.session_state.current_task_id = task.id
    st.session_state.start_time = time.time()
    st.session_state.hints_used = 0
    st.session_state.hint_index = 0
    st.session_state.submitted_task_id = None
    st.session_state.last_result = None


# --------------------------------------------------
# Display exercise
# --------------------------------------------------

st.divider()

st.subheader(task.title)

st.write(task.description)

st.caption(
    f"Difficulty: {task.difficulty}/5"
)

st.code(
    task.code,
    language="python",
)

st.write("**Your answer:**")

# --------------------------------------------------
# Hints
# --------------------------------------------------

if task.hints and st.session_state.hint_index < len(task.hints):

    if st.button("Show hint"):
        hint = task.hints[st.session_state.hint_index]

        st.session_state.hint_index += 1
        st.session_state.hints_used += 1

        st.info(hint)

        st.rerun()

elif task.hints:
    st.caption("You've used all available hints.")


# --------------------------------------------------
# Answer submission
# --------------------------------------------------

with st.form("answer_form"):

    submitted_answer = st.text_input(
        "Enter the expected output"
    )

    submitted = st.form_submit_button(
        "Submit answer"
    )


if submitted:

    if not submitted_answer.strip():
        st.warning("Please enter an answer.")

    elif st.session_state.submitted_task_id == task.id:
        st.warning("You've already submitted this exercise.")

    else:
        expected = task.expected_answer.strip().lower()
        actual = submitted_answer.strip().lower()

        is_correct = actual == expected

        duration = time.time() - st.session_state.start_time

        attempt = Attempt(
            id=str(uuid4()),
            learner_id=learner.id,
            task_id=task.id,
            submitted_answer=submitted_answer,
            is_correct=is_correct,
            hints_used=st.session_state.hints_used,
            duration_seconds=duration,
        )

        record_attempt(attempt)

        st.session_state.submitted_task_id = task.id
        st.session_state.last_result = is_correct


# --------------------------------------------------
# Feedback
# --------------------------------------------------

if st.session_state.submitted_task_id == task.id:

    if st.session_state.last_result:
        st.success("Correct! Well done.")
    else:
        st.error("Not quite. Here's the expected answer:")
        st.code(task.expected_answer)

    st.write(
        f"Hints used: {st.session_state.hints_used}"
    )

    st.write(
        f"Time taken: "
        f"{time.time() - st.session_state.start_time:.1f} seconds"
    )


# --------------------------------------------------
# Learner progress
# --------------------------------------------------

st.divider()

st.subheader("Your progress")

attempts = get_learner_attempts(learner.id)

total_attempts = len(attempts)

correct_attempts = sum(
    attempt.is_correct for attempt in attempts
)

accuracy = (
    correct_attempts / total_attempts * 100
    if total_attempts > 0
    else 0
)

col1, col2, col3 = st.columns(3)

col1.metric("Exercises completed", total_attempts)

col2.metric("Correct answers", correct_attempts)

col3.metric("Accuracy", f"{accuracy:.1f}%")
