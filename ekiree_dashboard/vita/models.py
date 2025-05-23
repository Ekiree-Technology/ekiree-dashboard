import hashlib

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field
from ed.models import Term
from localflavor.us.models import USStateField, USZipCodeField
from phonenumber_field.modelfields import PhoneNumberField

# TODO: Fix name of Menu_item and all references.
# TODO: Fix name of Home_page and all references.


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=8, blank=True)
    street = models.CharField(max_length=90, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = USStateField(blank=True)
    zip_code = USZipCodeField(blank=True, null=True)
    phone = PhoneNumberField(blank=True)
    mail_box = models.CharField(max_length=16, blank=True)
    domain = models.URLField(blank=True)
    advisor_email = models.EmailField(max_length=50, blank=True)
    sponsor_email = models.EmailField(max_length=50, blank=True)
    first_term = models.ForeignKey(
        Term,
        null=True,
        on_delete=models.SET_NULL,
        related_name="first_term_student_set",
    )
    grad_term = models.ForeignKey(
        Term,
        null=True,
        on_delete=models.SET_NULL,
        related_name="grade_term_student_set",
    )
    ED_meeting_complete = models.BooleanField(default=False)
    PR_meeting_complete = models.BooleanField(default=False)
    narrative = CKEditor5Field(blank=True, null=True)
    shared_url = models.CharField(max_length=64, blank=True)
    active = models.BooleanField(default=True)

    def sharable_hash(self):
        data = str(self.user.username).encode("utf-8")
        salt = str(self.user.password).encode("utf-8")
        return hashlib.sha256(data + salt).hexdigest()  # will be 64 characters

    def __repr__(self):
        return "<Student: %s>" % (self.user.username)

    def __str__(self):
        return "%s (%s %s)" % (
            self.user.username,
            self.user.first_name,
            self.user.last_name,
        )


class Application(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    essay = CKEditor5Field(blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True)
    last_submitted = models.DateTimeField(null=True, blank=True)
    submitted = models.BooleanField(default=False)
    resubmit = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    feedback = CKEditor5Field(blank=True, null=True)

    def __str__(self):
        return str(self.user.first_name) + " " + self.user.last_name

    def __repr__(self):
        return str(self.user.first_name) + " " + self.user.last_name + "<Application>"


class OffCampusExperience(models.Model):
    UNDECIDED = "UD"
    INTERNSHIP = "INT"
    COMMUNITY = "CBL"
    ABROAD = "STA"
    RESEARCH = "REU"
    OTHER = "OTR"
    EXPERIENCE_TYPE = (
        (UNDECIDED, "Undecided"),
        (INTERNSHIP, "Internship"),
        (COMMUNITY, "Community-Based Learning"),
        (ABROAD, "Study Abroad"),
        (RESEARCH, "Research Esperience for Undergraduates"),
        (OTHER, "Other"),
    )

    Y = "Yes"
    N = "No"
    BOOLEAN_ANSWER = (
        (Y, "Yes"),
        (N, "No"),
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
    )
    experience_type = models.CharField(
        max_length=3, choices=EXPERIENCE_TYPE, default="UD"
    )
    approved = models.CharField(max_length=3, choices=BOOLEAN_ANSWER, default="No")
    completed = models.CharField(max_length=3, choices=BOOLEAN_ANSWER, default="No")
    council_notes = CKEditor5Field(blank=True, null=True)
    reflection = CKEditor5Field(blank=True, null=True)

    def __str__(self):
        return str(self.student)


class Menu_item(models.Model):
    title = title = models.CharField(max_length=60)
    subtitle = models.CharField(max_length=120)
    link = models.CharField(max_length=60)
    thumbnail = models.ImageField(null=True)
    order = models.CharField(max_length=2)

    def __str__(self):
        return self.title


class Home_page(models.Model):
    image = models.ImageField(null=True)
    text = CKEditor5Field(blank=True, null=True)
    publish_date = models.DateTimeField(
        "Published",
        default=timezone.now,
    )
