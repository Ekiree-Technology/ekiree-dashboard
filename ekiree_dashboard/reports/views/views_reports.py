from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from ed.tools import all_courses, major_courses, minor_courses, WSPcourses, courses_by_division
from poetfolio.tools import is_student, is_WSPstaff, is_council, all_students
from siteconfig.models import get_hero_image


def ReportsIndex(request, username=None):
    user = request.user

    if request.method == "GET":
        if is_student(request.user):
            studentcourses = all_courses(user)
            major1 = major_courses(user, 1)
            major2 = major_courses(user, 2)
            minor1 = minor_courses(user, 1)
            minor2 = minor_courses(user, 2)
            wspcourses = WSPcourses(user)
            divcourses = courses_by_division(user)
            return render(
                request,
                "reports/reports.html",
                {
                    "pagename": request.user.get_full_name(),
                    "username": request.user.username,
                    "user": user,
                    "usercourses": studentcourses,
                    "divcourses": divcourses,
                    "wspcourses": wspcourses,
                    "major1": major1,
                    "major2": major2,
                    "minor1": minor1,
                    "minor2": minor2,
                    "hero": get_hero_image("reports"),
                },
            )
        elif is_WSPstaff(request.user) or is_council(request.user):
            if username is None:
                students = all_students()
                return render(
                    request,
                    "reports/studentpickerform.html",
                    {
                        "pagename": "Reports",
                        "target": "ReportsIndex",
                        "students": students,
                        "hero": get_hero_image("reports"),
                    },
                )

            else:
                user = User.objects.get(username=username)
                studentcourses = all_courses(user)
                divcourses = courses_by_division(user)
                wspcourses = WSPcourses(user)
                major1 = major_courses(user, 1)
                major2 = major_courses(user, 2)
                minor1 = minor_courses(user, 1)
                minor2 = minor_courses(user, 2)
                return render(
                    request,
                    "reports/reports.html",
                    {
                        "pagename": user.get_full_name(),
                        "username": user.username,
                        "user": user,
                        "usercourses": studentcourses,
                        "divcourses": divcourses,
                        "wspcourses": wspcourses,
                        "major1": major1,
                        "major2": major2,
                        "minor1": minor1,
                        "minor2": minor2,
                        "hero": get_hero_image("reports"),
                    },
                )
        else:
            return redirect(reverse("Index"))

    elif request.method == "POST":
        if is_WSPstaff(request.user) or is_council(request.user):
            student_id = request.POST.get("student")
            student = User.objects.get(id=student_id)
            return redirect(reverse("ReportsIndex") + student.username)
        else:
            return redirect(reverse("Index"))
    else:
        return redirect(reverse("Index"))
