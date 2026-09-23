from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SpreadDefinition:
    """A named reading pattern and the visual arrangement used to deal it."""

    name: str
    selector_label: str
    positions: tuple[str, ...]
    layout: str = "row"
    image_divisor: int = 2


# Ordered by card count, then from broad everyday readings toward deeper and
# more specialized work. Keeping the catalog as data makes new spreads easy to
# add without touching the drawing or interpretation code.
SPREADS = (
    SpreadDefinition("One Card", "ONE CARD — FOCUS", ("FOCUS",), image_divisor=0),
    SpreadDefinition(
        "Situation and Advice",
        "TWO CARD — SITUATION · ADVICE",
        ("SITUATION", "ADVICE"),
    ),
    SpreadDefinition(
        "Release and Receive",
        "TWO CARD — RELEASE · RECEIVE",
        ("RELEASE", "RECEIVE"),
    ),
    SpreadDefinition(
        "Choice and Cost",
        "TWO CARD — CHOICE · COST",
        ("WHAT I CHOOSE", "WHAT IT ASKS OF ME"),
    ),
    SpreadDefinition(
        "Past, Present, and Emerging",
        "THREE CARD — PAST · PRESENT · EMERGING",
        ("PAST", "PRESENT", "EMERGING"),
    ),
    SpreadDefinition(
        "Mind, Body, and Spirit",
        "THREE CARD — MIND · BODY · SPIRIT",
        ("MIND", "BODY", "SPIRIT"),
    ),
    SpreadDefinition(
        "Problem, Root, and Remedy",
        "THREE CARD — PROBLEM · ROOT · REMEDY",
        ("PROBLEM", "ROOT", "REMEDY"),
    ),
    SpreadDefinition(
        "Strength, Challenge, and Next Step",
        "THREE CARD — STRENGTH · CHALLENGE · NEXT STEP",
        ("STRENGTH", "CHALLENGE", "NEXT STEP"),
    ),
    SpreadDefinition(
        "Relationship Pulse",
        "THREE CARD — YOU · OTHER · CONNECTION",
        ("YOU", "OTHER", "CONNECTION"),
    ),
    SpreadDefinition(
        "Think, Feel, and Do",
        "THREE CARD — THINK · FEEL · DO",
        ("THINK", "FEEL", "DO"),
    ),
    SpreadDefinition(
        "Stop, Start, and Continue",
        "THREE CARD — STOP · START · CONTINUE",
        ("STOP", "START", "CONTINUE"),
    ),
    SpreadDefinition(
        "Daily Guidance",
        "THREE CARD — THEME · CAUTION · ACTION",
        ("THEME", "CAUTION", "ACTION"),
    ),
    SpreadDefinition(
        "Four-Card Guidance",
        "FOUR CARD — PRESENT · CHALLENGE · GUIDANCE · OUTCOME",
        ("PRESENT", "CHALLENGE", "GUIDANCE", "OUTCOME"),
        image_divisor=3,
    ),
    SpreadDefinition(
        "Situation, Advice, Avoid, and Outcome",
        "FOUR CARD — SITUATION · ADVICE · AVOID · OUTCOME",
        ("SITUATION", "ADVICE", "WHAT TO AVOID", "POSSIBLE OUTCOME"),
        image_divisor=3,
    ),
    SpreadDefinition(
        "Inner Conflict",
        "FOUR CARD — CONSCIOUS · HIDDEN · TENSION · INTEGRATION",
        ("CONSCIOUS WANT", "HIDDEN WANT", "SOURCE OF TENSION", "INTEGRATION"),
        image_divisor=3,
    ),
    SpreadDefinition(
        "Self-Love Check-In",
        "FOUR CARD — SELF · NEED · STRENGTH · CARE",
        ("RELATIONSHIP WITH SELF", "NEGLECTED NEED", "STRENGTH", "CARING ACTION"),
        image_divisor=3,
    ),
    SpreadDefinition(
        "New Connection",
        "FOUR CARD — ATTRACTION · PACING · SIGNAL · CONVERSATION",
        ("ATTRACTION", "PACING", "SIGNAL TO NOTICE", "HONEST CONVERSATION"),
        image_divisor=3,
    ),
    SpreadDefinition(
        "Lunar Reflection",
        "FOUR CARD — RELEASE · RETAIN · RECEIVE · INTEGRATE",
        ("RELEASE", "RETAIN", "RECEIVE", "INTEGRATE"),
        image_divisor=3,
    ),
    SpreadDefinition(
        "Five-Card Cross",
        "FIVE CARD — CROSS",
        ("PRESENT", "CHALLENGE", "PAST", "FUTURE", "POTENTIAL"),
        layout="cross",
        image_divisor=5,
    ),
    SpreadDefinition(
        "Shadow Work",
        "FIVE CARD — SHADOW WORK",
        ("RECURRING PATTERN", "HIDDEN ROOT", "PROTECTIVE PURPOSE", "PRESENT COST", "SAFE RESPONSE"),
        image_divisor=5,
    ),
    SpreadDefinition(
        "Career Path",
        "FIVE CARD — CAREER PATH",
        ("PRESENT POSITION", "UNDERUSED STRENGTH", "OBSTACLE", "PROMISING DIRECTION", "NEXT MOVE"),
        image_divisor=5,
    ),
    SpreadDefinition(
        "Healing After Heartbreak",
        "FIVE CARD — HEARTBREAK HEALING",
        ("WHAT HURTS", "WHAT LINGERS", "WHAT TO GRIEVE", "WHAT SUPPORTS ME", "WAY FORWARD"),
        image_divisor=5,
    ),
    SpreadDefinition(
        "Life Purpose",
        "FIVE CARD — LIFE PURPOSE",
        ("CORE GIFT", "DEEPEST VALUE", "WORK TO DO", "SERVICE", "NEXT EXPERIMENT"),
        image_divisor=5,
    ),
    SpreadDefinition(
        "Financial Health Check",
        "FIVE CARD — FINANCIAL HEALTH",
        ("CURRENT FOUNDATION", "MONEY PATTERN", "PRESSURE", "RESOURCE", "PRACTICAL STEP"),
        image_divisor=5,
    ),
    SpreadDefinition(
        "Goal Setting",
        "FIVE CARD — GOAL SETTING",
        ("TRUE GOAL", "MOTIVATION", "OBSTACLE", "RESOURCE", "FIRST MILESTONE"),
        image_divisor=5,
    ),
    SpreadDefinition(
        "Pros and Cons",
        "FIVE CARD — PROS · CONS · UNKNOWN · NEXT STEP",
        ("QUESTION", "BENEFIT", "COST", "UNKNOWN", "NEXT STEP"),
        image_divisor=5,
    ),
    SpreadDefinition(
        "Four Elements",
        "FIVE CARD — FOUR ELEMENTS",
        ("EARTH", "AIR", "FIRE", "WATER", "INTEGRATION"),
        layout="cross",
        image_divisor=5,
    ),
    SpreadDefinition(
        "Relationship Mirror",
        "SIX CARD — RELATIONSHIP MIRROR",
        ("MY ENERGY", "THEIR ENERGY", "SHARED DYNAMIC", "UNSPOKEN NEED", "NEEDED BOUNDARY", "GROWTH POTENTIAL"),
        layout="mirror",
        image_divisor=5,
    ),
    SpreadDefinition(
        "Business Idea",
        "SIX CARD — BUSINESS IDEA",
        ("CORE IDEA", "REAL NEED", "UNIQUE VALUE", "RESOURCE", "RISK", "SMALLEST TEST"),
        layout="grid",
        image_divisor=5,
    ),
    SpreadDefinition(
        "Personal Growth Pyramid",
        "SIX CARD — GROWTH PYRAMID",
        ("FOUNDATION", "LESSON", "ACTION", "SUPPORT", "EMERGING STRENGTH", "POTENTIAL"),
        layout="pyramid",
        image_divisor=5,
    ),
    SpreadDefinition(
        "Career Change",
        "SIX CARD — CAREER CHANGE",
        ("WHY CHANGE", "WHAT TO KEEP", "WHAT TO RELEASE", "READINESS", "RISK", "NEXT MOVE"),
        layout="grid",
        image_divisor=5,
    ),
    SpreadDefinition(
        "Creative Project",
        "SIX CARD — CREATIVE PROJECT",
        ("SPARK", "PURPOSE", "RESOURCE", "BLOCK", "EXPERIMENT", "POTENTIAL"),
        layout="grid",
        image_divisor=5,
    ),
    SpreadDefinition(
        "Seven-Card Horseshoe",
        "SEVEN CARD — HORSESHOE",
        ("PAST", "PRESENT", "HIDDEN INFLUENCE", "OBSTACLE", "ENVIRONMENT", "ADVICE", "OUTCOME"),
        layout="horseshoe",
        image_divisor=4,
    ),
    SpreadDefinition(
        "Two-Path Decision",
        "SEVEN CARD — TWO-PATH DECISION",
        ("CORE ISSUE", "PATH A — GIFT", "PATH A — COST", "PATH A — DIRECTION", "PATH B — GIFT", "PATH B — COST", "PATH B — DIRECTION"),
        layout="branches",
        image_divisor=6,
    ),
    SpreadDefinition(
        "Chakra Alignment",
        "SEVEN CARD — CHAKRA ALIGNMENT",
        ("ROOT", "SACRAL", "SOLAR PLEXUS", "HEART", "THROAT", "THIRD EYE", "CROWN"),
        layout="chakra",
        image_divisor=5,
    ),
    SpreadDefinition(
        "Week Ahead",
        "SEVEN CARD — WEEK AHEAD",
        ("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"),
        layout="horseshoe",
        image_divisor=4,
    ),
    SpreadDefinition(
        "Stay or Go",
        "SEVEN CARD — STAY OR GO",
        ("CORE NEED", "STAY — GIFT", "STAY — COST", "STAY — DIRECTION", "GO — GIFT", "GO — COST", "GO — DIRECTION"),
        layout="branches",
        image_divisor=6,
    ),
    SpreadDefinition(
        "Relationship Deep Dive",
        "SEVEN CARD — RELATIONSHIP DEEP DIVE",
        ("MY POSITION", "THEIR POSITION", "SHARED STRENGTH", "TENSION", "UNSPOKEN TRUTH", "NEEDED ACTION", "DIRECTION"),
        layout="horseshoe",
        image_divisor=4,
    ),
    SpreadDefinition(
        "Nine-Card Portrait",
        "NINE CARD — PORTRAIT",
        ("PAST MIND", "PRESENT MIND", "EMERGING MIND", "PAST HEART", "HEART OF MATTER", "EMERGING HEART", "PAST FOUNDATION", "PRESENT FOUNDATION", "EMERGING FOUNDATION"),
        layout="grid",
        image_divisor=7,
    ),
    SpreadDefinition(
        "Seasonal Compass",
        "NINE CARD — SEASONAL COMPASS",
        ("CENTER", "NORTH", "NORTHEAST", "EAST", "SOUTHEAST", "SOUTH", "SOUTHWEST", "WEST", "NORTHWEST"),
        layout="compass",
        image_divisor=7,
    ),
    SpreadDefinition(
        "Celtic Cross",
        "TEN CARD — CELTIC CROSS",
        ("PRESENT", "CROSSING INFLUENCE", "FOUNDATION", "PAST", "POSSIBILITY", "NEAR FUTURE", "SELF", "ENVIRONMENT", "HOPES AND FEARS", "DIRECTION"),
        layout="celtic_cross",
        image_divisor=8,
    ),
    SpreadDefinition(
        "Tree of Life",
        "TEN CARD — TREE OF LIFE",
        ("CROWN", "WISDOM", "UNDERSTANDING", "MERCY", "STRENGTH", "HARMONY", "DESIRE", "INTELLECT", "FOUNDATION", "MANIFESTATION"),
        layout="tree",
        image_divisor=8,
    ),
    SpreadDefinition(
        "Year Ahead",
        "TWELVE CARD — YEAR AHEAD",
        ("JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"),
        layout="wheel",
        image_divisor=8,
    ),
    SpreadDefinition(
        "Zodiac Wheel",
        "TWELVE CARD — ZODIAC WHEEL",
        ("SELF", "RESOURCES", "COMMUNICATION", "HOME", "CREATIVITY", "ROUTINE", "PARTNERSHIP", "TRANSFORMATION", "BELIEFS", "VOCATION", "COMMUNITY", "INNER LIFE"),
        layout="wheel",
        image_divisor=8,
    ),
)

SPREADS_BY_LABEL = {spread.selector_label: spread for spread in SPREADS}

