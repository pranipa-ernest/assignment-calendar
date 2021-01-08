import dotenv
import os

import requests


def get_calendar_entries():
    BASE_URL, PER_PAGE, auth_header = authorization()

    courses = get_courses(BASE_URL, PER_PAGE, auth_header)

    calendar_entries = get_course_assignments(BASE_URL, PER_PAGE, auth_header, courses)
    return calendar_entries


def get_course_assignments(BASE_URL, PER_PAGE, auth_header, courses):
    calendarEntries = dict()
    for course in courses:
        if 'access_restricted_by_date' in course:
            continue

        assignments_params = {}
        response = api_request(BASE_URL, PER_PAGE, auth_header, '/api/v1/courses/{}/assignments'.format(course["id"]),
                               assignments_params)
        assignments = get_assignments(response)
        # course code : [{list of assignment objects}]
        calendarEntries[course["course_code"]] = assignments
    return calendarEntries


def get_assignments(response):
    assignments = []
    for assignment in response:
        if assignment["due_at"] is not None:
            assignments.append({
                "name": assignment["name"],
                "description": clean_html(assignment["description"]) if
                assignment["description"] is not None else assignment["description"],
                "due_date": assignment["due_at"]
            })
    return assignments


def clean_html(raw_html):
    import re
    clean_r = re.compile('<.*?>')
    clean_text = re.sub(clean_r, '', raw_html)
    return clean_text


def get_courses(BASE_URL, PER_PAGE, auth_header):
    courses_params = {
        "state[]": "available"
    }
    courses = api_request(BASE_URL, PER_PAGE, auth_header, '/api/v1/courses', courses_params)
    return courses


def authorization():
    # load variables from .env file
    dotenv.load_dotenv(dotenv.find_dotenv())
    # Static settings
    BASE_URL = os.environ.get('CANVAS_URL', 'https://canvas.ubc.ca')
    PER_PAGE = int(os.environ.get('CANVAS_PER_PAGE', '100'))
    # ensure access token is available
    TOKEN = get_token()
    auth_header = {'Authorization': 'Bearer ' + TOKEN}  # setup the authorization header to be used later
    return BASE_URL, PER_PAGE, auth_header


def api_request(BASE_URL, PER_PAGE, auth_header, url, extra_params):
    page = 1
    request_obj = []
    while True:
        request_url = BASE_URL + url
        params = {
            "per_page": str(PER_PAGE),
            "page": str(page),
        }
        params.update(extra_params)
        r = requests.get(request_url, headers=auth_header, params=params)

        # always take care to handle request errors
        r.raise_for_status()  # raise error if 4xx or 5xx

        data = r.json()
        if len(data) == 0:
            break

        request_obj += data
        page += 1

    return request_obj


def get_token():
    TOKEN = os.environ.get('CANVAS_ACCESS_TOKEN')
    if TOKEN is None:
        print("No access token found. Please set `CANVAS_ACCESS_TOKEN`")
        exit()
    return TOKEN
