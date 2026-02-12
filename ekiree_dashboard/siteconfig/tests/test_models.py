from django.test import TestCase
from django.db.utils import IntegrityError
from ed.models import Subject, Course
from siteconfig.models import HeroImage, RequiredCourses


class HeroImageModelTest(TestCase):
    def test_saving_and_retrieving(self):
        hero = HeroImage.objects.create(app='ed')

        saved = HeroImage.objects.first()
        self.assertEqual(saved, hero)
        self.assertEqual(saved.app, 'ed')

    def test_str(self):
        hero = HeroImage.objects.create(app='vita')
        self.assertEqual(str(hero), 'vita')

    def test_app_is_unique(self):
        HeroImage.objects.create(app='ed')
        with self.assertRaises(IntegrityError):
            HeroImage.objects.create(app='ed')

    def test_default_app(self):
        hero = HeroImage()
        self.assertEqual(hero.app, 'default')


class RequiredCoursesModelTest(TestCase):
    def setUp(self):
        subject = Subject.objects.create(name='English', short='ENGL')
        self.course = Course.objects.create(
            subject=subject, number='120', title='Why Read?')

    def test_saving_and_retrieving(self):
        rc = RequiredCourses.objects.create(course=self.course, credits=3.0)

        saved = RequiredCourses.objects.first()
        self.assertEqual(saved, rc)
        self.assertEqual(saved.course, self.course)
        self.assertEqual(saved.credits, 3.0)

    def test_str(self):
        rc = RequiredCourses.objects.create(course=self.course, credits=3.0)
        self.assertIn('ENGL', str(rc))
        self.assertIn('Why Read?', str(rc))

    def test_cannot_save_without_course(self):
        rc = RequiredCourses(credits=3.0)
        with self.assertRaises(IntegrityError):
            rc.save()

    def test_cannot_save_without_credits(self):
        rc = RequiredCourses(course=self.course)
        with self.assertRaises(IntegrityError):
            rc.save()
