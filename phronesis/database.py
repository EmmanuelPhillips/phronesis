import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent.parent / "data" / "phronesis.db"


def get_connection(db_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    """Create a connection to the Phronesis database."""

    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database(db_path: Path = DATABASE_PATH) -> None:
    """Create the database tables if they do not already exist."""

    connection = get_connection(db_path)

    try:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS learners (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS skills (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                code TEXT NOT NULL,
                task_type TEXT NOT NULL,
                difficulty INTEGER NOT NULL CHECK (difficulty BETWEEN 1 AND 5),
                expected_answer TEXT NOT NULL,
                hints_json TEXT NOT NULL DEFAULT '[]'
            );

            CREATE TABLE IF NOT EXISTS task_skills (
                task_id TEXT NOT NULL,
                skill_id TEXT NOT NULL,
                PRIMARY KEY (task_id, skill_id),
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS attempts (
                id TEXT PRIMARY KEY,
                learner_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                submitted_answer TEXT NOT NULL,
                is_correct INTEGER NOT NULL CHECK (is_correct IN (0, 1)),
                hints_used INTEGER NOT NULL DEFAULT 0 CHECK (hints_used >= 0),
                duration_seconds REAL NOT NULL CHECK (duration_seconds >= 0),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (learner_id) REFERENCES learners(id),
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            );

            CREATE TABLE IF NOT EXISTS mastery (
                learner_id TEXT NOT NULL,
                skill_id TEXT NOT NULL,
                probability_known REAL NOT NULL
                    CHECK (probability_known BETWEEN 0 AND 1),
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (learner_id, skill_id),
                FOREIGN KEY (learner_id) REFERENCES learners(id) ON DELETE CASCADE,
                FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
            );
        """)

        connection.commit()

    finally:
        connection.close()
