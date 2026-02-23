from django.test import TestCase
from django.urls import reverse

from ed.models import Course, EDCourse, Subject, Term
from vita.models import Student

from reports.tests.helpers import make_user


class ReportsExportViewsTest(TestCase):
    def setUp(self):
        self.student = make_user("student", "Student")
        self.other_student = make_user("other_student", "Student")
        self.council = make_user("council", "Council")
        self.staff = make_user("staff", "WSP Staff")

        Student.objects.create(user=self.student, narrative="Test narrative")
        Student.objects.create(user=self.other_student, narrative="Other narrative")

        term = Term.objects.create(code=202009)
        subject = Subject.objects.create(name="English", short="ENGL")
        course = Course.objects.create(subject=subject, number="120", title="Why Read?")

        EDCourse.objects.create(student=self.student, course=course, term=term, credits=3)

    def test_csv_requires_login(self):
        response = self.client.get(reverse("CourseListCSV", args=[self.student.username]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_student_can_download_own_csv(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("CourseListCSV", args=[self.student.username]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn(
            f'attachment; filename="{self.student.username}_courselist.csv"',
            response["Content-Disposition"],
        )

    def test_student_cannot_download_another_students_csv(self):
        self.client.force_login(self.other_student)
        response = self.client.get(reverse("CourseListCSV", args=[self.student.username]))
        self.assertRedirects(response, reverse("Index"), fetch_redirect_response=False)

    def test_council_can_download_student_csv(self):
        self.client.force_login(self.council)
        response = self.client.get(reverse("CourseListCSV", args=[self.student.username]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")

    def test_pdf_requires_login(self):
        response = self.client.get(reverse("CourseListPDF", args=[self.student.username]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_student_can_download_own_pdf(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("CourseListPDF", args=[self.student.username]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn(
            f'filename="{self.student.username}_courselist.pdf"',
            response["Content-Disposition"],
        )

    def test_council_can_download_student_pdf(self):
        self.client.force_login(self.council)
        response = self.client.get(reverse("CourseListPDF", args=[self.student.username]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_staff_cannot_download_other_student_pdf(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("CourseListPDF", args=[self.student.username]))
        self.assertRedirects(response, reverse("Index"), fetch_redirect_response=False)
