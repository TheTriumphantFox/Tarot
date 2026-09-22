from __future__ import annotations

from collections.abc import Sequence

from .models import ReadingResult


SPREAD_POSITIONS = ("PAST", "PRESENT", "EMERGING")

_ARCHETYPES = {
    "major_00_the_fool": "agency",
    "major_01_the_magician": "agency",
    "major_02_the_high_priestess": "inward",
    "major_03_the_empress": "foundation",
    "major_04_the_emperor": "foundation",
    "major_05_the_hierophant": "foundation",
    "major_06_the_lovers": "connection",
    "major_07_the_chariot": "agency",
    "major_08_strength": "balance",
    "major_09_the_hermit": "inward",
    "major_10_wheel_of_fortune": "change",
    "major_11_justice": "balance",
    "major_12_the_hanged_man": "inward",
    "major_13_death": "change",
    "major_14_temperance": "balance",
    "major_15_the_devil": "shadow",
    "major_16_the_tower": "change",
    "major_17_the_star": "renewal",
    "major_18_the_moon": "inward",
    "major_19_the_sun": "renewal",
    "major_20_judgement": "renewal",
    "major_21_the_world": "completion",
}

_TRANSITIONS = {
    ("inward", "agency"): "private understanding is being asked to become a visible choice",
    ("agency", "inward"): "forward motion is being tempered by a need to listen and reconsider",
    ("foundation", "change"): "an established structure is meeting a change it cannot simply contain",
    ("change", "renewal"): "disruption is opening into repair, clarity, or renewed trust",
    ("change", "completion"): "a difficult transition is moving toward integration and closure",
    ("shadow", "renewal"): "what was bound or hidden is being brought into cleaner light",
    ("shadow", "agency"): "recognizing the binding pattern creates a practical point of choice",
    ("balance", "change"): "careful equilibrium is meeting a transition that requires adaptation",
    ("connection", "inward"): "a relationship or value-choice is asking for private honesty",
    ("connection", "balance"): "connection becomes sustainable through proportion and clear boundaries",
    ("renewal", "agency"): "renewed confidence is becoming readiness to act",
    ("completion", "agency"): "completion is clearing space for a new beginning",
    ("inward", "renewal"): "uncertainty or reflection is giving way to clearer hope",
    ("foundation", "connection"): "an existing structure is shaping the choice of how to meet another",
    ("discernment", "agency"): "a hard-won understanding is becoming a decision or visible action",
    ("agency", "discernment"): "enthusiasm is being tested by truth, consequence, or a need for precision",
    ("discernment", "connection"): "clear thinking is changing how emotion or relationship can be approached",
    ("connection", "discernment"): "feeling is asking to be named clearly rather than merely experienced",
    ("foundation", "discernment"): "practical conditions are bringing an important truth into focus",
    ("discernment", "foundation"): "insight is asking for a concrete form, boundary, or working plan",
}


def format_three_card_reading(results: Sequence[ReadingResult]) -> str:
    return format_spread_reading(results, SPREAD_POSITIONS)


def format_three_card_speech(results: Sequence[ReadingResult]) -> str:
    return format_spread_speech(results, SPREAD_POSITIONS)


def format_spread_reading(
    results: Sequence[ReadingResult],
    positions: Sequence[str],
) -> str:
    _validate_spread(results, positions)
    sections: list[str] = []
    for position, result in zip(positions, results, strict=True):
        orientation = "REVERSED" if result.reversed else "UPRIGHT"
        keywords = " · ".join(keyword.upper() for keyword in result.meaning.keywords)
        sections.append(
            f"{position.upper()} — {result.card.name.upper()} ({orientation})\n"
            f"{keywords}\n\n"
            f"{result.meaning.text}"
        )
    if any(
        marker in position.lower()
        for position in positions
        for marker in ("future", "outcome", "emerging", "potential", "possibility")
    ):
        sections.append(
            "Directional positions describe how the present pattern may develop, "
            "not a fixed prediction."
        )
    return "\n\n────────────────────────\n\n".join(sections)


def format_spread_speech(
    results: Sequence[ReadingResult],
    positions: Sequence[str],
) -> str:
    _validate_spread(results, positions)
    sections: list[str] = []
    for position, result in zip(positions, results, strict=True):
        orientation = "reversed" if result.reversed else "upright"
        sections.append(
            f"{position.title()}. {result.card.name}, {orientation}. "
            f"{result.meaning.text}"
        )
    if any(
        marker in position.lower()
        for position in positions
        for marker in ("future", "outcome", "emerging", "potential", "possibility")
    ):
        sections.append(
            "Directional positions describe how the present pattern may develop, "
            "not a fixed prediction."
        )
    return " ".join(sections)


def explain_relationship(results: Sequence[ReadingResult]) -> str:
    if len(results) != 3:
        raise ValueError("Relationship analysis requires exactly three results.")

    return explain_spread_relationship(results, SPREAD_POSITIONS)


def explain_spread_relationship(
    results: Sequence[ReadingResult],
    positions: Sequence[str],
) -> str:
    _validate_spread(results, positions)

    if len(results) == 2:
        movement = (
            f"The spread moves from {results[0].meaning.keywords[0]} in the "
            f"{positions[0].lower()} position toward {results[1].meaning.keywords[0]} "
            f"through {positions[1].lower()}."
        )
    else:
        middle = ", then ".join(
            f"{result.meaning.keywords[0]} through {position.lower()}"
            for position, result in zip(positions[1:-1], results[1:-1], strict=True)
        )
        movement = (
            f"The spread moves from {results[0].meaning.keywords[0]} in "
            f"{positions[0].lower()}, through {middle}, toward "
            f"{results[-1].meaning.keywords[0]} in {positions[-1].lower()}."
        )

    transitions = [
        _transition_sentence(first, second, first_position.title(), second_position.title())
        for first_position, second_position, first, second in zip(
            positions[:-1],
            positions[1:],
            results[:-1],
            results[1:],
            strict=True,
        )
    ]
    orientation = _orientation_sentence(results, positions)

    if len(results) == 3:
        center = (
            f"{results[1].card.name} is the hinge of the spread: its invitation toward "
            f"{results[1].meaning.keywords[0]} is what connects the earlier influence of "
            f"{results[0].card.name} with the direction suggested by {results[2].card.name}."
        )
        return " ".join((movement, *transitions, orientation, center))
    return " ".join((movement, *transitions, orientation))


def _transition_sentence(
    first: ReadingResult,
    second: ReadingResult,
    first_position: str,
    second_position: str,
) -> str:
    first_type = _archetype(first)
    second_type = _archetype(second)
    if first_type == second_type:
        return (
            f"{first_position} and {second_position} repeat the same broad archetypal "
            f"current, strengthening the link between {first.meaning.keywords[0]} and "
            f"{second.meaning.keywords[0]}."
        )
    transition = _TRANSITIONS.get((first_type, second_type))
    if transition:
        return (
            f"From {first_position} to {second_position}, {first.card.name} meeting "
            f"{second.card.name} suggests that {transition}."
        )
    return (
        f"From {first_position} to {second_position}, {first.card.name} establishes "
        f"the conditions that {second.card.name} answers, shifting the emphasis from "
        f"{first.meaning.keywords[0]} to {second.meaning.keywords[0]}."
    )


def _archetype(result: ReadingResult) -> str:
    major_type = _ARCHETYPES.get(result.card.id)
    if major_type:
        return major_type
    return {
        "wands": "agency",
        "cups": "connection",
        "swords": "discernment",
        "pentacles": "foundation",
    }.get(result.card.suit or "", "unknown")


def _orientation_sentence(
    results: Sequence[ReadingResult],
    positions: Sequence[str] = SPREAD_POSITIONS,
) -> str:
    count_name = {
        2: "two",
        3: "three",
        4: "four",
        5: "five",
        6: "six",
        7: "seven",
    }.get(len(results), str(len(results)))
    reversed_positions = [
        position
        for position, result in zip(positions, results, strict=True)
        if result.reversed
    ]
    if not reversed_positions:
        return (
            f"All {count_name} cards are upright, so the movement is comparatively direct and "
            "available for outward action."
        )
    if len(reversed_positions) == len(results):
        return (
            f"All {count_name} cards are reversed, placing the emphasis on an internal process, "
            "blocked expression, or a pattern that needs reconsideration before action."
        )
    if len(reversed_positions) == 1:
        return (
            f"The single reversal in the {reversed_positions[0].title()} position marks "
            "the pressure point where the spread is least direct and deserves extra attention."
        )
    joined = " and ".join(position.title() for position in reversed_positions)
    return (
        f"The reversals in the {joined} positions make those parts of the movement more "
        "internal, delayed, or dependent on a change in perspective."
    )


def _validate_spread(
    results: Sequence[ReadingResult],
    positions: Sequence[str],
) -> None:
    if len(results) < 2:
        raise ValueError("A spread interpretation requires at least two results.")
    if len(results) != len(positions):
        raise ValueError("Every card in a spread requires exactly one position.")
    if any(not position.strip() for position in positions):
        raise ValueError("Spread positions cannot be blank.")
