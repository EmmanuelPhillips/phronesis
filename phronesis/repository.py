import json
from uuid import uuid4
import sqlite3
from contextlib import closing
from pathlib import Path

from phronesis.database import DATABASE_PATH, get_connection
from phronesis.models import Learner, Skill, Task, Attempt
from phronesis.models import Attempt, Learner, Mastery, Skill, Task


def create_learner(
    name: str,
    db_path: Path = DATABASE_PATH,
    learner_id: str | None = None,
) -> Learner:

    learner = Learner(
        id=learner_id or str(uuid4()),
        name=name,
    )

    with closing(get_connection(db_path)) as connection:
        connection.execute(
            "INSERT INTO learners (id, name) VALUES (?, ?)",
            (learner.id, learner.name),
        )
        connection.commit()

    return learner

def get_learner(
    learner_id: str,
    db_path: Path = DATABASE_PATH,
) -> Learner | None:

    with closing(get_connection(db_path)) as connection:
        row = connection.execute(
            "SELECT * FROM learners WHERE id = ?",
            (learner_id,),
        ).fetchone()

    if row is None:
        return None

    from datetime import datetime

    return Learner(
        id=row["id"],
        name=row["name"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def create_skill(skill: Skill, db_path: Path = DATABASE_PATH) -> None:
    with closing(get_connection(db_path)) as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO skills (id, name, description)
            VALUES (?, ?, ?)
            """,
            (skill.id, skill.name, skill.description),
        )
        connection.commit()


def create_task(task: Task, db_path: Path = DATABASE_PATH) -> None:
    with closing(get_connection(db_path)) as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO tasks (
                id, title, description, code, task_type,
                difficulty, expected_answer, hints_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task.id,
                task.title,
                task.description,
                task.code,
                task.task_type,
                task.difficulty,
                task.expected_answer,
                json.dumps(task.hints),
            ),
        )

        for skill_id in task.skill_ids:
            connection.execute(
                """
                INSERT OR IGNORE INTO task_skills (task_id, skill_id)
                VALUES (?, ?)
                """,
                (task.id, skill_id),
            )

        connection.commit()


def get_all_tasks(db_path: Path = DATABASE_PATH) -> list[Task]:
    with closing(get_connection(db_path)) as connection:
        rows = connection.execute(
            """
            SELECT
                tasks.*,
                GROUP_CONCAT(task_skills.skill_id) AS skill_ids
            FROM tasks
            LEFT JOIN task_skills ON tasks.id = task_skills.task_id
            GROUP BY tasks.id
            ORDER BY tasks.id
            """
        ).fetchall()

    return [
        Task(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            code=row["code"],
            task_type=row["task_type"],
            difficulty=row["difficulty"],
            expected_answer=row["expected_answer"],
            skill_ids=row["skill_ids"].split(",") if row["skill_ids"] else [],
            hints=json.loads(row["hints_json"]),
        )
        for row in rows
    ]


def record_attempt(
    attempt: Attempt,
    db_path: Path = DATABASE_PATH,
) -> None:

    with closing(get_connection(db_path)) as connection:
        connection.execute(
            """
            INSERT INTO attempts (
                id, learner_id, task_id, submitted_answer,
                is_correct, hints_used, duration_seconds
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                attempt.id,
                attempt.learner_id,
                attempt.task_id,
                attempt.submitted_answer,
                int(attempt.is_correct),
                attempt.hints_used,
                attempt.duration_seconds,
            ),
        )
        connection.commit()


def get_learner_attempts(
    learner_id: str,
    db_path: Path = DATABASE_PATH,
) -> list[Attempt]:

    with closing(get_connection(db_path)) as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM attempts
            WHERE learner_id = ?
            ORDER BY created_at
            """,
            (learner_id,),
        ).fetchall()

    from datetime import datetime

    return [
        Attempt(
            id=row["id"],
            learner_id=row["learner_id"],
            task_id=row["task_id"],
            submitted_answer=row["submitted_answer"],
            is_correct=bool(row["is_correct"]),
            hints_used=row["hints_used"],
            duration_seconds=row["duration_seconds"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
        for row in rows
    ]


def get_mastery(
    learner_id: str,
    skill_id: str,
    db_path: Path = DATABASE_PATH,
) -> Mastery | None:
    """Retrieve a learner's mastery of a particular skill."""

    with closing(get_connection(db_path)) as connection:
        row = connection.execute(
            """
            SELECT learner_id, skill_id, probability_known
            FROM mastery
            WHERE learner_id = ? AND skill_id = ?
            """,
            (learner_id, skill_id),
        ).fetchone()

    if row is None:
        return None

    return Mastery(
        learner_id=row["learner_id"],
        skill_id=row["skill_id"],
        probability_known=row["probability_known"],
    )


def create_mastery(
    learner_id: str,
    skill_id: str,
    probability_known: float,
    db_path: Path = DATABASE_PATH,
) -> Mastery:
    """Create an initial mastery record for a learner and skill."""

    if not 0.0 <= probability_known <= 1.0:
        raise ValueError("Mastery must be between 0.0 and 1.0")

    mastery = Mastery(
        learner_id=learner_id,
        skill_id=skill_id,
        probability_known=probability_known,
    )

    with closing(get_connection(db_path)) as connection:
        connection.execute(
            """
            INSERT INTO mastery (
                learner_id,
                skill_id,
                probability_known
            )
            VALUES (?, ?, ?)
            """,
            (
                mastery.learner_id,
                mastery.skill_id,
                mastery.probability_known,
            ),
        )
        connection.commit()

    return mastery


def update_mastery_record(
    learner_id: str,
    skill_id: str,
    probability_known: float,
    db_path: Path = DATABASE_PATH,
) -> Mastery:
    """Update an existing mastery record."""

    if not 0.0 <= probability_known <= 1.0:
        raise ValueError("Mastery must be between 0.0 and 1.0")

    with closing(get_connection(db_path)) as connection:
        cursor = connection.execute(
            """
            UPDATE mastery
            SET probability_known = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE learner_id = ? AND skill_id = ?
            """,
            (probability_known, learner_id, skill_id),
        )

        if cursor.rowcount == 0:
            raise ValueError("Mastery record does not exist")

        connection.commit()

    return Mastery(
        learner_id=learner_id,
        skill_id=skill_id,
        probability_known=probability_known,
    )
