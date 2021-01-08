from datetime import timedelta, datetime
import pytz
from dateutil.tz import tz

import calendar_entries
import arrow
from ics import Calendar, Event, DisplayAlarm


def start_program():
    calender_entries = calendar_entries.get_calendar_entries()

    for course_code, assignments in calender_entries.items():
        create_calendar(course_code, assignments)


def create_calendar(course_code, assignments):
    c = Calendar()

    for assignment in assignments:
        event = create_entry(assignment)
        c.events.add(event)

    new_code = course_code.replace(" ", "_").replace("/", "_")
    with open(f"{new_code}.ics", 'w') as f:
        f.writelines(c)


def create_entry(assignment):
    e = Event()
    e.name = assignment["name"]
    # "2012-07-01T23:59:00-06:00"
    e.begin = arrow.get(assignment["due_date"]).replace(tzinfo='US/Pacific')
    e.make_all_day()
    e.description = assignment["description"]
    e.alarms = [DisplayAlarm(trigger=timedelta(days=-1))]
    return e


# def format_date(due_date):
#     eastern = due_date.tzinfo
#     pacific = 
#     return new_timezone_timestamp


if __name__ == '__main__':
    start_program()
