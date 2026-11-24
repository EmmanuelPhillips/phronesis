import time
from uuid import uuid4

import streamlit as st

from phronesis.models import Attempt
from phronesis.repository import (
    create_learner,
    get_learner,
    record_attempt,
)
from phronesis.seed import seed_database
from phronesis.learner_service import update_learner_mastery
from phronesis.task_selector import select_next_task
from phronesis.evaluation import evaluate_task


# --------------------------------------------------
# Application setup
# --------------------------------------------------

st.set_page_config(
    page_title="Phronesis",
    page_icon="🧠",
    layout="centered",
)

seed_database()

LEARNER_ID = "local-learner"

learner = get_learner(LEARNER_ID)

if learner is None:
    learner = create_learner(
        "Local learner",
        learner_id=LEARNER_ID,
    )


# --------------------------------------------------
# Session state
# --------------------------------------------------

if "current_task_id" not in st.session_state:
    st.session_state.current_task_id = None

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

if "hint_index" not in st.session_state:
    st.session_state.hint_index = 0

if "hints_used" not in st.session_state:
    st.session_state.hints_used = 0

if "last_result" not in st.session_state:
    st.session_state.last_result = None


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("Phronesis")
st.caption("Adaptive programming practice")

st.write(
    f"Welcome, {learner.name}. "
    "Your exercises adapt to your progress."
)

st.divider()


# --------------------------------------------------
# Previous attempt feedback
# --------------------------------------------------
if st.session_state.last_result is not None:
    result = st.session_state.last_result

    if result["correct"]:
        st.success(result["feedback"])
    else:
        st.error(result["feedback"])
        st.write(
            f"Expected answer: {result['expected_answer']}"
        )

    st.subheader("Updated skill mastery")

    for skill_id, probability in result["mastery"].items():
        st.write(f"**{skill_id}:** {probability:.1%}")

    st.divider()


# --------------------------------------------------
# Adaptive task selection
# --------------------------------------------------

task = select_next_task(LEARNER_ID)

if task is None:
    st.warning("There are currently no available tasks.")
    st.stop()


# --------------------------------------------------
# Reset task-specific state when task changes
# --------------------------------------------------

if st.session_state.current_task_id != task.id:
    st.session_state.current_task_id = task.id
    st.session_state.start_time = time.time()
    st.session_state.hint_index = 0
    st.session_state.hints_used = 0


# --------------------------------------------------
# Task display
# --------------------------------------------------

st.subheader(task.title)

st.write(task.description)

st.caption(
    f"Difficulty: {task.difficulty}/5"
)

st.code(task.code, language="python")


# --------------------------------------------------
# Hints
# --------------------------------------------------

if task.hints:
    st.subheader("Hints")

    # Display previously revealed hints.
    for index, hint in enumerate(
        task.hints[:st.session_state.hint_index],
        start=1,
    ):
        st.info(f"Hint {index}: {hint}")

    # Reveal the next hint.
    if st.session_state.hint_index < len(task.hints):
        if st.button("Show hint"):
            st.session_state.hint_index += 1
            st.session_state.hints_used += 1
            st.rerun()


# --------------------------------------------------
# Answer submission
# --------------------------------------------------

with st.form("answer_form"):
    submitted_answer = st.text_area(
    "Your answer",
    key=f"answer_{task.id}"
)

    submitted = st.form_submit_button("Submit answer")

    if submitted:
        if not submitted_answer.strip():
            st.warning("Please enter an answer.")
        else:
            evaluation_result = evaluate_task(
            task,
            submitted_answer,
            )

            is_correct = evaluation_result.is_correct

            duration = time.time() - st.session_state.start_time

            attempt = Attempt(
                id=str(uuid4()),
                learner_id=LEARNER_ID,
                task_id=task.id,
                submitted_answer=submitted_answer,
                is_correct=is_correct,
                hints_used=st.session_state.hints_used,
                duration_seconds=duration,
            )

            # Record the completed attempt.
            record_attempt(attempt)

            # Update mastery for the skills associated
            # with the completed task.
            updated_mastery = update_learner_mastery(
                attempt,
                task.skill_ids,
            )

            # Save feedback for the next Streamlit rerun.
            st.session_state.last_result = {
                "correct": is_correct,
                "feedback": evaluation_result.feedback,
                "task_title": task.title,
                "expected_answer": evaluation_result.expected_answer,
                "mastery": {
                    record.skill_id: record.probability_known
                    for record in updated_mastery
                },
            }

            # Reset exercise-specific state.
            st.session_state.hint_index = 0
            st.session_state.hints_used = 0
            st.session_state.start_time = time.time()

            st.rerun()
