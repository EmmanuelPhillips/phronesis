import sqlite3

from phronesis.database import get_connection, initialize_database


def test_database_initialization(tmp_path):
    db_path = tmp_path / "test.db"

    initialize_database(db_path)

    connection = get_connection(db_path)

    try:
        tables = connection.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
        """).fetchall()

        table_names = {row["name"] for row in tables}

        assert {
            "learners",
            "skills",
            "tasks",
            "task_skills",
            "attempts",
            "mastery",
        }.issubset(table_names)

    finally:
        connection.close()


def test_database_enforces_foreign_keys(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)

    connection = get_connection(db_path)

    try:
        try:
            connection.execute("""
                INSERT INTO attempts (
                    id, learner_id, task_id, submitted_answer,
                    is_correct, hints_used, duration_seconds
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("attempt-1", "missing-learner", "missing-task",
                  "answer", 1, 0, 10))

            assert False, "Expected a foreign key constraint failure"

        except sqlite3.IntegrityError:
            pass

    finally:
        connection.close()
