from django.test import TestCase
from django.urls import reverse

from ed.models import EducationalGoal, Major, Minor
from ed.tests.helpers import make_course, make_edcourse, make_term, make_user
from vita.models import Student


class GoalViewsTest(TestCase):
    def setUp(self):
        self.student = make_user("student", "Student")
        self.other_student = make_user("other_student", "Student")

        term = make_term()
        course = make_course("ENGL", "English", "120", "Why Read?")
        self.edcourse = make_edcourse(self.student, course=course, term=term, credits=3)
        self.goal = EducationalGoal.objects.create(
            student=self.student,
            title="Original",
            description="Original description",
        )
        self.goal.courses.add(self.edcourse)

    def test_student_can_view_add_goal_page(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("AddGoal"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ed/EducationalGoalForm.html")

    def test_student_can_create_goal(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("AddGoal"),
            {
                "title": "New Goal",
                "description": "desc",
                "courses": [str(self.edcourse.id)],
            },
        )
        self.assertRedirects(response, reverse("AddGoal"), fetch_redirect_response=False)
        self.assertTrue(EducationalGoal.objects.filter(student=self.student, title="New Goal").exists())

    def test_edit_goal_get_requires_owner(self):
        self.client.force_login(self.other_student)
        response = self.client.get(reverse("EditGoal", args=[self.goal.id]))
        self.assertRedirects(response, reverse("EDIndex"), fetch_redirect_response=False)

    def test_edit_goal_post_invalid_does_not_update(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("EditGoal", args=[self.goal.id]),
            {
                "title": "X" * 81,
                "description": "updated",
                "courses": [str(self.edcourse.id)],
            },
        )
        self.assertRedirects(response, reverse("EDIndex"), fetch_redirect_response=False)
        self.goal.refresh_from_db()
        self.assertEqual(self.goal.title, "Original")

    def test_edit_goal_post_valid_updates_goal(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("EditGoal", args=[self.goal.id]),
            {
                "title": "Updated",
                "description": "updated",
                "courses": [str(self.edcourse.id)],
            },
        )
        self.assertRedirects(response, reverse("AllGoals"), fetch_redirect_response=False)
        self.goal.refresh_from_db()
        self.assertEqual(self.goal.title, "Updated")

    def test_delete_goal_post_removes_goal(self):
        self.client.force_login(self.student)
        response = self.client.post(reverse("deleteEducationalGoal"), {"egoal_id": self.goal.id})
        self.assertRedirects(response, reverse("AddGoal"), fetch_redirect_response=False)
        self.assertFalse(EducationalGoal.objects.filter(id=self.goal.id).exists())


class MajorMinorViewsTest(TestCase):
    def setUp(self):
        self.student = make_user("student", "Student")
        self.council = make_user("council", "Council")

        term = make_term()
        course = make_course("ENGL", "English", "120", "Why Read?")
        self.edcourse = make_edcourse(self.student, course=course, term=term, credits=3)

    def test_student_can_view_major_minor_page(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("MajorMinor"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ed/MajorMinorForm.html")

    def test_non_student_redirected_from_major_minor(self):
        self.client.force_login(self.council)
        response = self.client.get(reverse("MajorMinor"))
        self.assertRedirects(response, reverse("Index"), fetch_redirect_response=False)

    def test_student_can_create_major_minor_on_post(self):
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("MajorMinor"),
            {
                "maj1title": "Math",
                "maj1summary": "Math major",
                "maj2title": "",
                "maj2summary": "",
                "min1title": "History",
                "min1summary": "History minor",
                "min2title": "",
                "min2summary": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Major.objects.filter(student=self.student, number=1).exists())
        self.assertTrue(Minor.objects.filter(student=self.student, number=1).exists())

    def test_delete_major_clears_flags_and_deletes_major(self):
        major = Major.objects.create(student=self.student, title="Math", description="desc", number=1)
        self.edcourse.maj1 = True
        self.edcourse.save(update_fields=["maj1"])

        self.client.force_login(self.student)
        response = self.client.post(reverse("deleteMajor"), {"major_id": 1})
        self.assertRedirects(response, reverse("CourseList"), fetch_redirect_response=False)

        self.edcourse.refresh_from_db()
        self.assertFalse(self.edcourse.maj1)
        self.assertFalse(Major.objects.filter(id=major.id).exists())

    def test_delete_minor_clears_flags_and_deletes_minor(self):
        minor = Minor.objects.create(
            student=self.student,
            title="History",
            description="desc",
            number=1,
        )
        self.edcourse.min1 = True
        self.edcourse.save(update_fields=["min1"])

        self.client.force_login(self.student)
        response = self.client.post(reverse("deleteMinor"), {"minor_id": 1})
        self.assertRedirects(response, reverse("CourseList"), fetch_redirect_response=False)

        self.edcourse.refresh_from_db()
        self.assertFalse(self.edcourse.min1)
        self.assertFalse(Minor.objects.filter(id=minor.id).exists())


class SharedListViewTest(TestCase):
    def setUp(self):
        self.student = make_user("student", "Student")
        Student.objects.create(user=self.student, shared_url="abc123")
        term = make_term()
        course = make_course("ENGL", "English", "120", "Why Read?")
        make_edcourse(self.student, course=course, term=term, credits=3)

    def test_missing_shared_url_redirects_index(self):
        response = self.client.get(reverse("SharedList"))
        self.assertRedirects(response, reverse("Index"), fetch_redirect_response=False)

    def test_valid_shared_url_renders_shared_list(self):
        response = self.client.get(reverse("SharedList", args=["abc123"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ed/sharedlist.html")
