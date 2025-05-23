from django import forms
from django.conf import settings
from vita.models import *
from phonenumber_field.formfields import PhoneNumberField
from django_ckeditor_5.widgets import CKEditor5Widget
from localflavor.us.forms import USStateSelect, USZipCodeField

class StudentNarrativeForm(forms.ModelForm):
    narrative = forms.CharField(widget=CKEditor5Widget())
    class Meta:
        model = Student
        fields = ('narrative',)

class StudentInfoForm(forms.ModelForm):
    phone = PhoneNumberField(region=getattr(settings, "PHONENUMBER_DEFAULT_REGION", None))
    class Meta:
        model = Student
        fields = ('student_id',
                  'street',
                  'city',
                  'state',
                  'zip_code',
                  'phone',
                  'mail_box',
                  'domain',
                  'advisor_email',
                  'sponsor_email',
                  'first_term',
                  'grad_term',
                 )

class ApplicationForm(forms.ModelForm):
    essay = forms.CharField(widget=CKEditor5Widget())
    class Meta:
        model = Application
        fields = ('essay',
                 )

class ApplicationFeedbackForm(forms.ModelForm):
    feedback = forms.CharField(widget=CKEditor5Widget())
    class Meta:
        model = Application
        fields = ('feedback',
                 )

class OffCampusReflectForm(forms.ModelForm):
    reflection = forms.CharField(widget=CKEditor5Widget())
    class Meta:
        model = OffCampusExperience
        fields = ('experience_type',
                  'completed',
                'reflection',
                 )

class OffCampusCouncilNotesForm(forms.ModelForm):
    council_notes = forms.CharField(widget=CKEditor5Widget())
    class Meta:
        model = OffCampusExperience
        fields = ('approved',
                  'council_notes',
                 )
