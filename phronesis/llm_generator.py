import ollama

from phronesis.task_generation import parse_generated_tasks
from phronesis.task_verification import verify_task


TASK_SCHEMA = {
    "type": "object",
    "properties": {
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "code": {"type": "string"},
                    "task_type": {
                        "type": "string",
                        "enum": ["predict_output"],
                    },
                    "difficulty": {
                        "type": "integer",
                        "enum": [1, 2, 3],
                    },
                    "expected_answer": {"type": "string"},
                    "skill_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "hints": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": [
                    "title",
                    "description",
                    "code",
                    "task_type",
                    "difficulty",
                    "expected_answer",
                    "skill_ids",
                    "hints",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": ["tasks"],
    "additionalProperties": False,
}


class OllamaTaskGenerator:
    def __init__(self, client=None, model="qwen2.5-coder:7b"):
        self.client = client or ollama.Client()
        self.model = model

    def generate_tasks(
        self,
        topic: str,
        skill_ids: list[str],
        valid_skill_ids: set[str],
        difficulty: int,
        count: int = 5,
        existing_task_ids: set[str] | None = None,
        max_attempts: int = 3,
    ):
        if not topic.strip():
            raise ValueError("Topic cannot be empty.")

        if not skill_ids:
            raise ValueError("At least one skill must be specified.")

        if not set(skill_ids).issubset(valid_skill_ids):
            raise ValueError("Unknown skill IDs were supplied.")

        if difficulty not in (1, 2, 3):
            raise ValueError("Difficulty must be between 1 and 3.")

        if not 1 <= count <= 10:
            raise ValueError("Count must be between 1 and 10.")

        if not 1 <= max_attempts <= 5:
            raise ValueError("Maximum attempts must be between 1 and 5.")

        instructions = """
        You are an educational programming question generator.

        Generate Python code-tracing questions for learners.

        Requirements:
        - Generate original questions, not trivial variations.
        - Every question must contain valid Python code.
        - Every expected_answer must exactly match stdout.
        - Use the requested difficulty level.
        - Only use the supplied skill IDs.
        - Each question should assess the supplied skills.
        - Provide two progressive hints without revealing the answer.
        - Keep questions unambiguous and suitable for beginners.
        """

        verified_tasks = []
        rejection_feedback = []

        for attempt in range(max_attempts):
            remaining = count - len(verified_tasks)

            if remaining == 0:
                break

            request = f"""
            Generate exactly {remaining} Python code-tracing questions.

            Topic: {topic}

            Available skill IDs: {skill_ids}

            Required difficulty: {difficulty}

            Only generate predict_output tasks.

            Do not repeat questions from previous attempts.

            Previous verification feedback:
            {rejection_feedback}
            """

            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": instructions,
                    },
                    {
                        "role": "user",
                        "content": request,
                    },
                ],
                format=TASK_SCHEMA,
                options={"temperature": 0},
            )


            response_text = response.message.content

            if not response_text:
                raise ValueError("The LLM returned an empty response.")

            generated_tasks = parse_generated_tasks(
                response_text,
                valid_skill_ids,
                existing_task_ids,
            )

            if len(generated_tasks) != remaining:
                raise ValueError(
                    f"Expected {remaining} tasks but received "
                    f"{len(generated_tasks)}."
                )

            for task in generated_tasks:
                result = verify_task(task)

                if result.is_valid:
                    verified_tasks.append(task)
                else:
                    rejection_feedback.append(
                        f"Rejected '{task.title}': {result.error}"
                    )

                if len(verified_tasks) == count:
                    break

        if len(verified_tasks) != count:
            raise RuntimeError(
                f"Could only generate {len(verified_tasks)} "
                f"verified tasks out of {count} after "
                f"{max_attempts} attempts. "
                f"Feedback: {rejection_feedback}"
            )

        return verified_tasks
