from pathlib import Path

from phronesis.database import DATABASE_PATH
from phronesis.knowledge_tracing import (
    BKTParameters,
    update_mastery,
)
from phronesis.models import Attempt, Mastery
from phronesis.repository import (
    create_mastery,
    get_mastery,
    update_mastery_record,
)


def update_learner_mastery(
    attempt: Attempt,
    skill_ids: list[str],
    db_path: Path = DATABASE_PATH,
    parameters: BKTParameters | None = None,
) -> list[Mastery]:
    """
    Update a learner's mastery estimates based on an attempt.

    Each skill associated with the task receives a BKT update.
    """

    if parameters is None:
        parameters = BKTParameters()

    updated_records = []

    for skill_id in skill_ids:
        current_mastery = get_mastery(
            attempt.learner_id,
            skill_id,
            db_path,
        )

        if current_mastery is None:
            probability_known = parameters.initial_mastery

            create_mastery(
                attempt.learner_id,
                skill_id,
                probability_known,
                db_path,
            )
        else:
            probability_known = current_mastery.probability_known

        new_probability = update_mastery(
            probability_known,
            attempt.is_correct,
            parameters,
        )

        updated_record = update_mastery_record(
            attempt.learner_id,
            skill_id,
            new_probability,
            db_path,
        )

        updated_records.append(updated_record)

    return updated_records
