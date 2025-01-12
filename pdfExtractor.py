import pdfplumber
import json


def extract_schedule(pdf_path: str):
    c = 0
    courses = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            if c == 0:
                table = page.extract_table()
                if table is not None:
                    for nc in table[2:]:
                        course = {}
                        course["name"] = str(nc[2]).replace('\n', ' ')
                        course["section"] = str(nc[6])

                        course_schedule = nc[9].replace('\n', ' ')
                        course_schedule = course_schedule.replace('- ', '-')

                        l = course_schedule.split(' ')
                        number_schedules = len(l) // 6
                        if len(l) % 6 != 0:
                            number_schedules += 1
                        course["schedule"] = [{} for i in range(number_schedules)]

                        for i in range(number_schedules):
                            course["schedule"][i]["day"] = l[i * 6 + 2]
                            course["schedule"][i]["type"] = l[i * 6 + 3]
                            try:
                                course["schedule"][i]["hour"] = l[i * 6 + 4]
                                course["schedule"][i]["classroom"] = l[i * 6 + 5]
                            except IndexError:
                                course["schedule"][i]["hour"] = ""
                                course["schedule"][i]["classroom"] = ""
                        courses.append(course)
            else:
                table = page.extract_table()
                if table is not None:
                    for nc in table:
                        if nc[0:8] == [''] * 8:
                            laggard = nc[9].split(' ')
                            courses[len(courses) - 1]["schedule"][len(courses[len(courses) - 1]["schedule"]) - 1][
                                "hour"] = \
                                laggard[0]
                            courses[len(courses) - 1]["schedule"][len(courses[len(courses) - 1]["schedule"]) - 1][
                                "classroom"] = laggard[1]
                            continue
                        course = {}
                        course["name"] = str(nc[2]).replace('\n', ' ')
                        course["section"] = str(nc[6])

                        course_schedule = nc[9].replace('\n', ' ')
                        course_schedule = course_schedule.replace('- ', '-')

                        l = course_schedule.split(' ')
                        number_schedules = len(l) // 6
                        if len(l) % 6 != 0:
                            number_schedules += 1
                        course["schedule"] = [{} for i in range(number_schedules)]

                        for i in range(number_schedules):
                            course["schedule"][i]["day"] = l[i * 6 + 2]
                            course["schedule"][i]["type"] = l[i * 6 + 3]
                            try:
                                course["schedule"][i]["hour"] = l[i * 6 + 4]
                                course["schedule"][i]["classroom"] = l[i * 6 + 5]
                            except IndexError:
                                course["schedule"][i]["hour"] = ""
                                course["schedule"][i]["classroom"] = ""
                        courses.append(course)
            c += 1

    with open("courses.json", "w") as f:
        json.dump(courses, f, indent=4)
