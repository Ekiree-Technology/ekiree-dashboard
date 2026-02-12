from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from vita.models import Student, Application, OffCampusExperience, Menu_item, Home_page


class StudentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_student',
            password='testpass',
            first_name='Test',
            last_name='Student',
        )

    def test_saving_and_retrieving_student(self):
        student = Student(user=self.user, student_id='12345678')
        student.save()

        saved = Student.objects.first()
        self.assertEqual(saved, student)
        self.assertEqual(saved.user, self.user)
        self.assertEqual(saved.student_id, '12345678')
        self.assertTrue(saved.active)

    def test_str(self):
        student = Student.objects.create(user=self.user)
        self.assertEqual(str(student), 'test_student (Test Student)')

    def test_repr(self):
        student = Student.objects.create(user=self.user)
        self.assertEqual(repr(student), '<Student: test_student>')

    def test_sharable_hash_is_consistent(self):
        student = Student.objects.create(user=self.user)
        hash1 = student.sharable_hash()
        hash2 = student.sharable_hash()
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)

    def test_cannot_save_without_user(self):
        student = Student()
        with self.assertRaises(IntegrityError):
            student.save()

    def test_defaults(self):
        student = Student.objects.create(user=self.user)
        self.assertFalse(student.ED_meeting_complete)
        self.assertFalse(student.PR_meeting_complete)
        self.assertTrue(student.active)
        self.assertEqual(student.street, '')
        self.assertEqual(student.city, '')


class ApplicationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_student',
            password='testpass',
            first_name='Test',
            last_name='Student',
        )

    def test_saving_and_retrieving_application(self):
        app = Application.objects.create(user=self.user, essay='My essay')

        saved = Application.objects.first()
        self.assertEqual(saved, app)
        self.assertEqual(saved.user, self.user)
        self.assertEqual(saved.essay, 'My essay')

    def test_str(self):
        app = Application.objects.create(user=self.user)
        self.assertEqual(str(app), 'Test Student')

    def test_defaults(self):
        app = Application.objects.create(user=self.user)
        self.assertFalse(app.submitted)
        self.assertFalse(app.resubmit)
        self.assertFalse(app.accepted)
        self.assertFalse(app.rejected)
        self.assertIsNone(app.last_submitted)

    def test_can_save_without_user(self):
        app = Application.objects.create()
        self.assertIsNone(app.user)


class OffCampusExperienceModelTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            username='test_student', password='testpass')
        self.student = Student.objects.create(user=user)

    def test_saving_and_retrieving(self):
        exp = OffCampusExperience.objects.create(
            student=self.student,
            experience_type='INT',
        )

        saved = OffCampusExperience.objects.first()
        self.assertEqual(saved, exp)
        self.assertEqual(saved.student, self.student)
        self.assertEqual(saved.experience_type, 'INT')

    def test_defaults(self):
        exp = OffCampusExperience.objects.create(student=self.student)
        self.assertEqual(exp.experience_type, 'UD')
        self.assertEqual(exp.approved, 'No')
        self.assertEqual(exp.completed, 'No')

    def test_str(self):
        exp = OffCampusExperience.objects.create(student=self.student)
        self.assertEqual(str(exp), str(self.student))

    def test_cannot_save_without_student(self):
        exp = OffCampusExperience()
        with self.assertRaises(IntegrityError):
            exp.save()


class MenuItemModelTest(TestCase):
    def test_saving_and_retrieving(self):
        item = Menu_item.objects.create(
            title='Test',
            subtitle='A subtitle',
            link='/test/',
            order='1',
        )

        saved = Menu_item.objects.first()
        self.assertEqual(saved, item)
        self.assertEqual(saved.title, 'Test')

    def test_str(self):
        item = Menu_item.objects.create(
            title='My Title',
            subtitle='sub',
            link='/',
            order='1',
        )
        self.assertEqual(str(item), 'My Title')


class HomePageModelTest(TestCase):
    def test_saving_and_retrieving(self):
        page = Home_page.objects.create(text='Hello world')

        saved = Home_page.objects.first()
        self.assertEqual(saved, page)
        self.assertEqual(saved.text, 'Hello world')
        self.assertIsNotNone(saved.publish_date)
