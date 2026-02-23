from django.test import TestCase
from django.urls import reverse

from ed.models import ApprovedCourse
from ed.tests.helpers import make_course, make_edcourse, make_term, make_user
from vita.models import Student


class EDViewRoleBranchesTest(TestCase):
    def setUp(self):
        self.student = make_user("student", "Student")
        self.council = make_user("council", "Council")
        self.staff = make_user("staff", "WSP Staff")
        self.target = make_user("target", "Student")

        term = make_term()
        course = make_course("ENGL", "English", "120", "Why Read?")
        make_edcourse(self.target, course=course, term=term, credits=3)

    def test_council_get_without_username_sees_picker(self):
        self.client.force_login(self.council)
        response = self.client.get(reverse("ED"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ed/studentpickerform.html")

    def test_staff_get_with_username_sees_ed_page(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("ED", args=[self.target.username]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ed/ED.html")
        self.assertEqual(response.context["user"], self.target)

    def test_council_post_with_valid_student_redirects_to_target(self):
        self.client.force_login(self.council)
        response = self.client.post(reverse("ED"), {"student": self.target.id})
        self.assertRedirects(
            response,
            reverse("ED", args=[self.target.username]),
            fetch_redirect_response=False,
        )

    def test_council_post_with_invalid_student_redirects_back(self):
        self.client.force_login(self.council)
        response = self.client.post(reverse("ED"), {"student": 999999})
        self.assertRedirects(response, reverse("ED"), fetch_redirect_response=False)

    def test_student_post_redirects_to_index(self):
        self.client.force_login(self.student)
        response = self.client.post(reverse("ED"), {"student": self.target.id})
        self.assertRedirects(response, reverse("Index"), fetch_redirect_response=False)


class ApproveEDViewTest(TestCase):
    def setUp(self):
        self.staff = make_user("staff", "WSP Staff")
        self.student = make_user("student", "Student")

        Student.objects.create(user=self.student)

        term = make_term()
        course_a = make_course("ENGL", "English", "120", "Why Read?")
        course_b = make_course("BIOL", "Biology", "151", "Cell Biology")

        self.edcourse_a = make_edcourse(self.student, course=course_a, term=term, credits=3)
        self.edcourse_b = make_edcourse(self.student, course=course_b, term=term, credits=4)

    def test_non_staff_cannot_approve_ed(self):
        self.client.force_login(self.student)
        response = self.client.post(reverse("ApproveED"), {"student": self.student.username})
        self.assertRedirects(response, reverse("Index"), fetch_redirect_response=False)

    def test_staff_can_approve_selected_courses_and_create_approved_courses(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("ApproveED"),
            {
                "student": self.student.username,
                str(self.edcourse_a): "on",
            },
        )

        self.assertRedirects(
            response,
            reverse("ApprovedCourses") + self.student.username,
            fetch_redirect_response=False,
        )

        self.edcourse_a.refresh_from_db()
        self.edcourse_b.refresh_from_db()
        self.assertTrue(self.edcourse_a.approved)
        self.assertFalse(self.edcourse_b.approved)

        self.assertTrue(
            ApprovedCourse.objects.filter(student=self.student, course=self.edcourse_a.course).exists()
        )
        self.assertFalse(
            ApprovedCourse.objects.filter(student=self.student, course=self.edcourse_b.course).exists()
        )

    def test_staff_unchecking_course_deletes_stale_approved_course(self):
        ApprovedCourse.objects.create(
            student=self.student,
            course=self.edcourse_b.course,
            term=self.edcourse_b.term,
            credits=self.edcourse_b.credits,
        )

        self.client.force_login(self.staff)
        self.client.post(
            reverse("ApproveED"),
            {
                "student": self.student.username,
                str(self.edcourse_a): "on",
            },
        )

        self.assertTrue(
            ApprovedCourse.objects.filter(student=self.student, course=self.edcourse_a.course).exists()
        )
        self.assertFalse(
            ApprovedCourse.objects.filter(student=self.student, course=self.edcourse_b.course).exists()
        )
