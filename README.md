# Phronesis

An adaptive programming practice platform designed to improve
code comprehension through personalised exercises and AI-assisted feedback.

## Goal

Develop a proof of concept that demonstrates how Bayesian Knowledge
Tracing and AI-generated programming exercises can adapt practice
to a learner's individual areas of difficulty.

## Planned features

- Adaptive learner modelling using Bayesian Knowledge Tracing
- Programming exercise generation and validation
- Personalised exercise selection
- AI-assisted hints and feedback
- Progress tracking and mastery estimates

## Tech stack

- Python
- Streamlit
- SQLite
- Large Language Models
- Pytest

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/main.py
