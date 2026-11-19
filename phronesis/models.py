from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class Skill:
    id: str
    name: str
    description: str


@dataclass
class Task:
    id: str
    title: str
    description: str
    code: str
    task_type: str
    difficulty: int
    expected_answer: str
    skill_ids: list[str]
    hints: list[str] = field(default_factory=list)


@dataclass
class Learner:
    id: str
    name: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Attempt:
    id: str
    learner_id: str
    task_id: str
    submitted_answer: str
    is_correct: bool
    hints_used: int
    duration_seconds: float
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Mastery:
    learner_id: str
    skill_id: str
    probability_known: float
