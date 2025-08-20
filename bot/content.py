import random
from dataclasses import dataclass
from typing import List, Dict, Literal, Tuple

RenderType = Literal["time_of_day", "text_card", "clock"]


@dataclass
class Question:
    question_text: str
    choices: List[str]
    correct: str
    render_type: RenderType
    render_params: Dict


TIMES_OF_DAY: List[str] = ["утро", "день", "вечер", "ночь"]
DAYS_OF_WEEK: List[str] = [
    "понедельник",
    "вторник",
    "среда",
    "четверг",
    "пятница",
    "суббота",
    "воскресенье",
]
MONTHS: List[str] = [
    "январь",
    "февраль",
    "март",
    "апрель",
    "май",
    "июнь",
    "июль",
    "август",
    "сентябрь",
    "октябрь",
    "ноябрь",
    "декабрь",
]
SEASON_BY_MONTH_INDEX: Dict[int, str] = {
    0: "зима",
    1: "зима",
    2: "весна",
    3: "весна",
    4: "весна",
    5: "лето",
    6: "лето",
    7: "лето",
    8: "осень",
    9: "осень",
    10: "осень",
    11: "зима",
}
SEASONS: List[str] = ["зима", "весна", "лето", "осень"]


def _unique_choices(options: List[str], correct: str, total: int = 4) -> List[str]:
    pool = [o for o in options if o != correct]
    random.shuffle(pool)
    distractors = pool[: max(0, total - 1)]
    result = distractors + [correct]
    random.shuffle(result)
    return result


def _level1_time_of_day() -> Question:
    label = random.choice(TIMES_OF_DAY)
    q = "Что изображено на картинке? Выбери время суток."
    choices = _unique_choices(TIMES_OF_DAY, label)
    return Question(
        question_text=q,
        choices=choices,
        correct=label,
        render_type="time_of_day",
        render_params={"label": label},
    )


def _level2_days_of_week() -> Question:
    mode = random.choice(["after", "before", "today_if_yesterday"])
    if mode == "after":
        start_index = random.randrange(0, 7)
        day = DAYS_OF_WEEK[start_index]
        correct = DAYS_OF_WEEK[(start_index + 1) % 7]
        q = f"Что идёт после: {day}?"
        render = {"text": f"После какого дня?\n{day}"}
    elif mode == "before":
        start_index = random.randrange(0, 7)
        day = DAYS_OF_WEEK[start_index]
        correct = DAYS_OF_WEEK[(start_index - 1) % 7]
        q = f"Что идёт перед: {day}?"
        render = {"text": f"Перед каким днём?\n{day}"}
    else:
        # today_if_yesterday
        yesterday_index = random.randrange(0, 7)
        yesterday = DAYS_OF_WEEK[yesterday_index]
        correct = DAYS_OF_WEEK[(yesterday_index + 1) % 7]
        q = f"Если вчера был {yesterday}, то какой день сегодня?"
        render = {"text": f"Вчера был:\n{yesterday}"}

    choices = _unique_choices(DAYS_OF_WEEK, correct)
    return Question(
        question_text=q,
        choices=choices,
        correct=correct,
        render_type="text_card",
        render_params=render,
    )


def _level3_months_and_seasons() -> Question:
    mode = random.choice(["season_of_month", "next_month"])
    if mode == "season_of_month":
        month_index = random.randrange(0, 12)
        month = MONTHS[month_index]
        correct = SEASON_BY_MONTH_INDEX[month_index]
        q = f"К какому времени года относится месяц: {month}?"
        choices = _unique_choices(SEASONS, correct)
        render = {"text": f"Месяц:\n{month}"}
    else:
        month_index = random.randrange(0, 12)
        month = MONTHS[month_index]
        correct = MONTHS[(month_index + 1) % 12]
        q = f"Что идёт после месяца: {month}?"
        choices = _unique_choices(MONTHS, correct)
        render = {"text": f"Месяц:\n{month}"}

    return Question(
        question_text=q,
        choices=choices,
        correct=correct,
        render_type="text_card",
        render_params=render,
    )


def _random_hours() -> int:
    hour = random.randint(1, 12)
    return hour


def _level4_whole_hours() -> Question:
    hour = _random_hours()
    minute = 0
    correct = f"{hour}:00"
    q = "Сколько времени на часах?"

    # Build distractors: nearby hours
    options = {correct}
    while len(options) < 4:
        delta = random.choice([-2, -1, 1, 2, 3, -3])
        h = ((hour + delta - 1) % 12) + 1
        options.add(f"{h}:00")
    choices = list(options)
    random.shuffle(choices)

    return Question(
        question_text=q,
        choices=choices,
        correct=correct,
        render_type="clock",
        render_params={"hour": hour, "minute": minute},
    )


def _level5_quarters_and_halves() -> Question:
    hour = _random_hours()
    minute = random.choice([15, 30, 45])
    correct = f"{hour}:{minute:02d}"
    q = "Сколько времени на часах?"

    # Distractors: same hour, different among 15/30/45 plus neighbor hour same minute
    options = {correct}
    candidates = [15, 30, 45]
    for m in candidates:
        options.add(f"{hour}:{m:02d}")
    neighbor_hour = ((hour % 12) + 1)
    options.add(f"{neighbor_hour}:{minute:02d}")
    # Ensure size 4
    while len(options) < 4:
        options.add(f"{random.randint(1,12)}:{random.choice(candidates):02d}")
    choices = list(options)
    random.shuffle(choices)

    return Question(
        question_text=q,
        choices=choices,
        correct=correct,
        render_type="clock",
        render_params={"hour": hour, "minute": minute},
    )


def generate_question(level: int) -> Question:
    if level <= 1:
        return _level1_time_of_day()
    if level == 2:
        return _level2_days_of_week()
    if level == 3:
        return _level3_months_and_seasons()
    if level == 4:
        return _level4_whole_hours()
    return _level5_quarters_and_halves()
