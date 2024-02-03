import os
import json
import dateparser
from datetime import datetime, timedelta, timezone

DATA_DIR = 'data'


def get_assignment_dict(title, course, due_date, link, submitted, late_due_date=None):
    return {
        'title': title,
        'course': course,
        'dueDate': dateparser.parse(due_date).strftime('%Y%m%dT%H%M%SZ'),  # sets to pseudo utc time
        'lateDueDate': dateparser.parse(late_due_date[14:]).strftime('%Y%m%dT%H%M%SZ') if late_due_date else None,
        'link': link,
        'submitted': submitted
    }


def save_data(var_name, obj):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    target = os.path.join(DATA_DIR, var_name + '.json')
    with open(target, 'w') as file:
        file.write(f'{json.dumps(obj, indent=2)}')


def json_to_ics(time_offset, json_path=os.path.join(DATA_DIR, 'assignments.json')):
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)
    ics_str = """BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//github.com/jakobz5404/Gradescope-iCal-Integration//EN\nCALSCALE:GREGORIAN\n"""
    ics_str += "X-WR-CALNAME:Gradescope Assignments\n"
    uid = 1
    for course, course_assignments in data.items():
        for assignment in course_assignments:
            if not assignment['submitted']:
                uid = uid + 1
                if time_offset == 0:
                    time = assignment['dueDate']
                else:
                    time = datetime.strftime(
                        datetime.strptime(assignment['dueDate']) + timedelta(minutes=int(time_offset * 60)))
                event_details = (f"BEGIN:VEVENT\n"
                                 f"SUMMARY:{assignment['title']}\n"
                                 f"DTSTART:{time}\n"
                                 f"DTEND:{time}\n"
                                 f"LOCATION:{assignment['course']}\n"
                                 f"URL:{assignment['link']}\n"
                                 f"UID:{uid}\n"
                                 f"END:VEVENT\n")
                ics_str += event_details
                if assignment['lateDueDate']:
                    uid = uid + 1
                    if time_offset == 0:
                        time = assignment['lateDueDate']
                    else:
                        time = datetime.strftime(
                            datetime.strptime(assignment['lateDueDate']) + timedelta(minutes=int(time_offset * 60)))
                    event_details = (f"BEGIN:VEVENT\n"
                                     f"SUMMARY:{'Late Due Date: ' + assignment['title']}\n"
                                     f"DTSTART:{time}\n"
                                     f"DTEND:{time}\n"
                                     f"LOCATION:{assignment['course']}\n"
                                     f"URL:{assignment['link']}\n"
                                     f"UID:{uid}\n"
                                     f"END:VEVENT\n")
                    ics_str += event_details
    ics_str += "END:VCALENDAR\n"
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    target = os.path.join(DATA_DIR, 'assignments.ics')
    with open(target, 'w') as file:
        file.write(ics_str)


def old_cleaner(json_path=os.path.join(DATA_DIR, 'assignments.json'), cutoff=180):
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)
    cutoff_date = datetime.now() - timedelta(days=cutoff)
    data.items()
    for course, course_assignments in data.items():
        # Filter assignments that are newer than cutoff_date
        data[course] = [
            assignment for assignment in course_assignments
            if datetime.strptime(assignment['lateDueDate'] if assignment['lateDueDate'] else assignment['dueDate'],
                                 "%Y%m%dT%H%M%SZ") >= cutoff_date
        ]
    save_data("assignments", data)
