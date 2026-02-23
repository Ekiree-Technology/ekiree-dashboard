from django.contrib.auth.models import Group, User

from ed.models import Course, EDCourse, Subject, Term


def make_user(username, group_name=None, password="testpass"):
    user = User.objects.create_user(username=username, password=password)
    if group_name:
        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)
    return user


def make_course(short="ENGL", name="English", number="120", title="Why Read?"):
    subject, _ = Subject.objects.get_or_create(short=short, defaults={"name": name})
    if subject.name != name:
        subject.name = name
        subject.save(update_fields=["name"])
    return Course.objects.create(subject=subject, number=number, title=title)


def make_term(code=202009):
    return Term.objects.create(code=code)


def make_edcourse(student, course=None, term=None, credits=3):
    if course is None:
        course = make_course()
    return EDCourse.objects.create(
        student=student,
        course=course,
        term=term,
        credits=credits,
    )
