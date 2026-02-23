from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from ed.models import ApprovedCourse
from ed.tests.helpers import make_course, make_edcourse, make_term, make_user


class ApprovedCourseViewsTest(TestCase):
    def setUp(self):
        self.student = make_user("student", "Student")
        self.other_student = make_user("other_student", "Student")
        self.council = make_user("council", "Council")
        self.staff = make_user("staff", "WSP Staff")

        term = make_term()
        self.course_a = make_course("ENGL", "English", "120", "Why Read?")
        self.course_b = make_course("BIOL", "Biology", "151", "Cell Biology")

        self.student_edcourse = make_edcourse(
            self.student,
            course=self.course_a,
            term=term,
            credits=3,
        )
        self.other_edcourse = make_edcourse(
            self.other_student,
            course=self.course_b,
            term=term,
            credits=4,
        )

        self.student_approved = ApprovedCourse.objects.create(
            student=self.student,
            course=self.course_a,
            term=term,
            credits=3,
        )

    def test_approved_courses_requires_login(self):
        response = self.client.get(reverse("ApprovedCourses"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_student_can_view_approved_courses(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("ApprovedCourses"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ed/approvedcourses.html")

    def test_student_post_to_approved_courses_redirects_index(self):
        self.client.force_login(self.student)
        response = self.client.post(reverse("ApprovedCourses"), {"student": self.student.id})
        self.assertRedirects(response, reverse("Index"), fetch_redirect_response=False)

    def test_staff_get_approved_courses_without_username_shows_picker(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("ApprovedCourses"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ed/studentpickerform.html")

    def test_council_post_to_approved_courses_redirects_to_student_username(self):
        self.client.force_login(self.council)
        response = self.client.post(reverse("ApprovedCourses"), {"student": self.student.id})
        self.assertRedirects(
            response,
            reverse("ApprovedCourses", args=[self.student.username]),
            fetch_redirect_response=False,
        )

    def test_council_post_with_unknown_student_redirects_back(self):
        self.client.force_login(self.council)
        response = self.client.post(reverse("ApprovedCourses"), {"student": 99999})
        self.assertRedirects(response, reverse("ApprovedCourses"), fetch_redirect_response=False)

    def test_student_can_replace_own_approved_course(self):
        self.client.force_login(self.student)
        payload = {"replacement": str(self.student_edcourse.id), "reason": "new reason"}
        response = self.client.post(
            reverse("replaceAppCourse", args=[self.student_approved.id]),
            payload,
        )
        self.assertRedirects(response, reverse("ApprovedCourses"), fetch_redirect_response=False)

        self.student_approved.refresh_from_db()
        self.assertEqual(self.student_approved.replacement, self.student_edcourse)
        self.assertEqual(self.student_approved.reason, "new reason")

    def test_student_cannot_replace_other_students_approved_course(self):
        other_approved = ApprovedCourse.objects.create(
            student=self.other_student,
            course=self.course_b,
            term=self.student_edcourse.term,
            credits=4,
        )
        self.client.force_login(self.student)
        response = self.client.post(
            reverse("replaceAppCourse", args=[other_approved.id]),
            {"replacement": str(self.student_edcourse.id), "reason": "x"},
        )
        self.assertRedirects(response, reverse("Index"), fetch_redirect_response=False)

        other_approved.refresh_from_db()
        self.assertIsNone(other_approved.replacement)


class ApproveReplacementViewTest(TestCase):
    def setUp(self):
        self.student = make_user("student", "Student")
        self.other_student = make_user("other_student", "Student")
        self.council = make_user("council", "Council")

        term = make_term()
        self.course_a = make_course("ENGL", "English", "120", "Why Read?")
        self.course_b = make_course("BIOL", "Biology", "151", "Cell Biology")

        self.original_edcourse = make_edcourse(self.student, self.course_a, term, 3)
        self.replacement_edcourse = make_edcourse(self.student, self.course_b, term, 4)

        self.approved_course = ApprovedCourse.objects.create(
            student=self.student,
            course=self.course_a,
            term=term,
            credits=3,
            replacement=self.replacement_edcourse,
            reason="replace this",
        )

    def test_anonymous_user_cannot_approve_replacements(self):
        response = self.client.post(reverse("approveReplace"), {"replace": "1", "course_id": self.approved_course.id})
        self.assertEqual(response.status_code, 302)

    def test_student_cannot_approve_replacements(self):
        self.client.force_login(self.student)
        response = self.client.post(reverse("approveReplace"), {"replace": "1", "course_id": self.approved_course.id})
        self.assertRedirects(response, reverse("Index"), fetch_redirect_response=False)

    def test_council_replace_flow_swaps_course(self):
        self.client.force_login(self.council)
        response = self.client.post(
            reverse("approveReplace"),
            {
                "replace": "1",
                "course_id": str(self.approved_course.id),
                "newcourse_id": str(self.replacement_edcourse.id),
            },
            HTTP_REFERER=reverse("ApprovedCourses"),
        )
        self.assertRedirects(response, reverse("ApprovedCourses"), fetch_redirect_response=False)

        self.assertFalse(ApprovedCourse.objects.filter(id=self.approved_course.id).exists())
        self.assertTrue(
            ApprovedCourse.objects.filter(
                student=self.student,
                course=self.replacement_edcourse.course,
            ).exists()
        )

    def test_council_can_approve_pending_edcourse(self):
        pending = make_edcourse(self.other_student, self.course_b, self.original_edcourse.term, 4)
        self.client.force_login(self.council)

        response = self.client.post(
            reverse("approveReplace"),
            {"course_id": str(pending.id)},
            HTTP_REFERER=reverse("ApprovedCourses"),
        )
        self.assertRedirects(response, reverse("ApprovedCourses"), fetch_redirect_response=False)
        self.assertTrue(
            ApprovedCourse.objects.filter(student=self.other_student, course=self.course_b).exists()
        )
