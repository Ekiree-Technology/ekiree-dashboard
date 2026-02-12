from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.urls import reverse
from vita.models import Student, Application, OffCampusExperience


class VitaIndexViewTest(TestCase):
    def setUp(self):
        student_group = Group.objects.create(name='Student')
        self.student = User.objects.create_user(
            username='test_student', password='testpass')
        self.student.groups.add(student_group)

        council_group = Group.objects.create(name='Council')
        self.council = User.objects.create_user(
            username='test_council', password='testpass')
        self.council.groups.add(council_group)

    def test_anonymous_redirects_to_login(self):
        response = self.client.get(reverse('VitaIndex'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_student_can_view(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('VitaIndex'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vitabase.html')

    def test_student_auto_creates_student_and_application(self):
        self.client.force_login(self.student)
        self.client.get(reverse('VitaIndex'))

        self.assertTrue(Student.objects.filter(user=self.student).exists())
        self.assertTrue(Application.objects.filter(user=self.student).exists())

    def test_council_can_view(self):
        self.client.force_login(self.council)
        response = self.client.get(reverse('VitaIndex'))
        self.assertEqual(response.status_code, 200)


class VitaNarrativeViewTest(TestCase):
    def setUp(self):
        student_group = Group.objects.create(name='Student')
        self.student = User.objects.create_user(
            username='test_student', password='testpass')
        self.student.groups.add(student_group)
        Student.objects.create(user=self.student, narrative='My narrative')

    def test_anonymous_redirects_to_login(self):
        response = self.client.get(reverse('VitaNarrative'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_student_can_view_narrative(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('VitaNarrative'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vita/narrative.html')
        self.assertEqual(response.context['narrative'], 'My narrative')


class VitaInfoViewTest(TestCase):
    def setUp(self):
        student_group = Group.objects.create(name='Student')
        self.student = User.objects.create_user(
            username='test_student', password='testpass')
        self.student.groups.add(student_group)
        Student.objects.create(user=self.student)

        council_group = Group.objects.create(name='Council')
        self.council = User.objects.create_user(
            username='test_council', password='testpass')
        self.council.groups.add(council_group)

    def test_anonymous_redirects_to_login(self):
        response = self.client.get(reverse('VitaInfo'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_student_can_view_own_info(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('VitaInfo'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vita/info.html')

    def test_council_sees_student_picker(self):
        self.client.force_login(self.council)
        response = self.client.get(reverse('VitaInfo'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vita/studentpickerform.html')


class VitaApplicationViewTest(TestCase):
    def setUp(self):
        student_group = Group.objects.create(name='Student')
        self.student = User.objects.create_user(
            username='test_student', password='testpass')
        self.student.groups.add(student_group)
        Student.objects.create(user=self.student)
        Application.objects.create(user=self.student)

        council_group = Group.objects.create(name='Council')
        self.council = User.objects.create_user(
            username='test_council', password='testpass')
        self.council.groups.add(council_group)

    def test_anonymous_redirects_to_login(self):
        response = self.client.get(reverse('VitaApplication'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_student_can_view_application(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse('VitaApplication'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vita/application.html')

    def test_council_sees_applications_list(self):
        self.client.force_login(self.council)
        response = self.client.get(reverse('VitaApplication'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vita/viewapplications.html')
