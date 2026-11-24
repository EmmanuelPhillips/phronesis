from dataclasses import dataclass


@dataclass
class BKTParameters:
    initial_mastery: float = 0.20
    learning_rate: float = 0.10
    guess_probability: float = 0.20
    slip_probability: float = 0.10


def update_mastery(
    probability_known: float,
    is_correct: bool,
    parameters: BKTParameters,
) -> float:
    """Update a learner's mastery probability after an attempt."""

    # Probability of observing the answer given mastery.
    if is_correct:
        likelihood_known = 1 - parameters.slip_probability
        likelihood_unknown = parameters.guess_probability
    else:
        likelihood_known = parameters.slip_probability
        likelihood_unknown = 1 - parameters.guess_probability

    # Bayesian update.
    numerator = probability_known * likelihood_known
    denominator = numerator + (
        (1 - probability_known) * likelihood_unknown
    )

    posterior = numerator / denominator

    # Account for learning during the attempt.
    updated_mastery = posterior + (
        (1 - posterior) * parameters.learning_rate
    )

    return updated_mastery
