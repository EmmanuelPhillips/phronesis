from phronesis.llm_generator import OllamaTaskGenerator


generator = OllamaTaskGenerator()

tasks = generator.generate_tasks(
    topic="Python loops and iteration",
    skill_ids=["loops"],
    valid_skill_ids={
        "code-tracing",
        "conditionals",
        "loops",
    },
    difficulty=2,
    count=3,
)

for task in tasks:
    print(f"\n{task.title}")
    print(task.code)
    print(f"Expected output: {task.expected_answer}")
    print(f"Hints: {task.hints}")
