from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.urls import reverse


class EnterStudentsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user', password='testpass')

    def test_anonymous_redirects_to_login(self):
        response = self.client.get(reverse('EnterStudents'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_authenticated_user_can_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('EnterStudents'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'siteconfig/EnterStudents.html')
