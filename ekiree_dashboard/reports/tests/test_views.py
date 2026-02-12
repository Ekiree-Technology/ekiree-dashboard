from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.urls import reverse


class ReportsIndexViewTest(TestCase):
    def setUp(self):
        student_group = Group.objects.create(name='Student')
        self.student = User.objects.create_user(
            username='test_student', password='testpass')
        self.student.groups.add(student_group)

        council_group = Group.objects.create(name='Council')
        self.council = User.objects.create_user(
            username='test_council', password='testpass')
        self.council.groups.add(council_group)

        wspstaff_group = Group.objects.create(name='WSP Staff')
        self.wspstaff = User.objects.create_user(
            username='test_wspstaff', password='testpass')
        self.wspstaff.groups.add(wspstaff_group)

    def test_student_can_view_reports(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('ReportsIndex'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/reports.html')

    def test_council_sees_student_picker(self):
        self.client.force_login(self.council)
        response = self.client.get(reverse('ReportsIndex'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/studentpickerform.html')

    def test_wspstaff_sees_student_picker(self):
        self.client.force_login(self.wspstaff)
        response = self.client.get(reverse('ReportsIndex'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/studentpickerform.html')

    def test_unauthenticated_user_redirects(self):
        self.client.force_login(
            User.objects.create_user(username='nobody', password='testpass'))
        response = self.client.get(reverse('ReportsIndex'), follow=True)
        self.assertEqual(response.status_code, 200)
