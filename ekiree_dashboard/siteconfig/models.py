from django.db import models
from ed.models import Course

# Create your models here.


def get_hero_image(app):
    """Fetch the HeroImage for the given app name, or None if it doesn't exist.

    This must be called inside view functions (not at module level) to avoid
    database queries at import time, which breaks manage.py commands that run
    before migrations.
    """
    try:
        return HeroImage.objects.get(app=app)
    except HeroImage.DoesNotExist:
        return None


class HeroImage(models.Model):
    DEFAULT = "default"
    ED = "ed"
    VITA = "vita"
    REPORTS = "reports"
    APP_CHOICES = [
        (DEFAULT, "default"),
        (ED, "ed"),
        (VITA, "vita"),
        (REPORTS, "reports"),
    ]
    hero = models.ImageField()
    app = models.CharField(
        unique=True,
        choices=APP_CHOICES,
        default=DEFAULT,
        max_length=10,
    )

    def __str__(self):
        return self.app


class RequiredCourses(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
    )

    credits = models.FloatField()

    def __str__(self):
        the_str = str(self.course) + ": " + self.course.title
        return the_str

    def __repr__(self):
        the_repr = str(self.course) + " (" + self.student.username + ")"
        return the_repr
