#!/Usr/bin/env python
# import numpy as np
import re
import datetime
from subprocess import run
import pyperclip
import argparse


# @title Функции
#
def get_empty_slots(meetings):
    # массив бул - занята ли минута?
    minutes_day = [False] * (60 * 24)

    for meeting in meetings:
        # прсим время из строчки
        start, finish = re.findall(r"\d{1,2}:\d{1,2}", meeting)
        start_minute = int(start.split(":")[0]) * 60 + int(start.split(":")[1])
        finish_minute = int(finish.split(":")[0]) * 60 + int(finish.split(":")[1])
        start_t = datetime.datetime.strptime(start, "%H:%M").time()
        # Заносим встречу в массив
        minutes_day[start_minute : finish_minute + 1] = [True] * (
            finish_minute - start_minute + 1
        )

    empty_slots_tuples = extract_false_slots(minutes_day)

    empty_slots = [tuple_to_slot(slot) for slot in empty_slots_tuples]

    return empty_slots


def extract_false_slots(arr, found_slots=None, start_idx=0):
    if found_slots is None:
        found_slots = []
    try:
        first_false_idx = arr.index(False, start_idx)
    except ValueError as e:
        # не нашли незанятую минутку
        return found_slots

    # нашли незанятую минутку

    try:
        first_true_idx = arr.index(True, first_false_idx)

    except ValueError as e:
        # не нашли конец
        new_slot = (first_false_idx, len(arr) - 1)
        found_slots.append(new_slot)
        return found_slots

    # нашли конец
    new_slot = (first_false_idx, first_true_idx - 1)
    found_slots.append(new_slot)
    return extract_false_slots(arr, found_slots, first_true_idx)


assert extract_false_slots([False, False]) == [(0, 1)]
assert extract_false_slots([False, False, True]) == [(0, 1)]
assert extract_false_slots([False, False, True, True]) == [(0, 1)]
assert extract_false_slots([False, False, True, False]) == [(0, 1), (3, 3)]
assert extract_false_slots([True, True, True, True]) == []


def tuple_to_slot(slot):
    def int_to_time(x):
        return f"{x//60:02d}:{x%60:02d}"

    return int_to_time(slot[0]) + " " + int_to_time(slot[1])


assert get_empty_slots(["11:10 - 12:00"]) == ["00:00 11:09", "12:01 23:59"]
assert get_empty_slots(["11:10 - 12:00", "13:40 16:00"]) == [
    "00:00 11:09",
    "12:01 13:39",
    "16:01 23:59",
]


current_time = datetime.datetime.now().time().replace(second=0, microsecond=0)
current_date = str(datetime.datetime.now().date())
parser = argparse.ArgumentParser(
    description="Для получения слотов на текущий день - не используйте аргументы, для получения слотов на любой день - используйте аргумент -d"
)
parser.add_argument(
    "-d", type=str, default=current_date, help=" год-месяц-день например 2024-11-28 "
)
my_namespace = parser.parse_args()
# print(my_namespace.d)


result = run(
    f'/usr/local/bin/icalBuddy -nrd -npn -nc -eep "title, location, url, notes, attendees, date" eventsFrom:{my_namespace.d} to:{my_namespace.d} ',
    shell=True,
    capture_output=True,
    encoding="UTF-8",
)

result = result.stdout
print(f"Ответ икалбадди {result}\n\n")
meet = [x[1:-1] for x in result.split("•") if x != ""]

print(f"Список встреч {meet}\n\n")

if my_namespace.d == current_date:
    busy_t_early = "00:00 - " + str(current_time)
else:
    busy_t_early = "00:00 - 10:00"

busy_t_late = "19:00 - 23:59"

meet.append(busy_t_late)

meet[0] = busy_t_early
slots = get_empty_slots(meet)
print(f"Список встреч 2 {meet}\n\n")
# print(meet)
slots2 = "".join("• c " + str(x).replace(" ", " по ") + "\n" for x in slots)

print(
    f"На {str(current_time).replace(':00','')} {current_date} у меня (s.kogan@bft.ru) пустые следующие слоты на {my_namespace.d}:\n{slots2}"
)

pyperclip.copy(
    f"На {str(current_time).replace(':00','')} {current_date} у меня (s.kogan@bft.ru) пустые следующие слоты на {my_namespace.d}:\n{slots2}"
)
