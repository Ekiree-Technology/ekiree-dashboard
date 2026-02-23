from django.contrib.auth.models import Group, User

from vita.models import Application, OffCampusExperience, Student


def make_user(username, group_name=None, password="testpass"):
    user = User.objects.create_user(username=username, password=password)
    if group_name:
        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)
    return user


def make_student_profile(username="student", group_name="Student"):
    user = make_user(username, group_name)
    student = Student.objects.create(user=user)
    Application.objects.create(user=user)
    off_campus = OffCampusExperience.objects.create(student=student)
    return user, student, off_campus
