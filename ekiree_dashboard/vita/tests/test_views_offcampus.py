from django.test import TestCase
from django.urls import reverse

from vita.models import OffCampusExperience
from vita.tests.helpers import make_student_profile, make_user


class VitaEditNarrativeViewTest(TestCase):
    def setUp(self):
        self.student_user, self.student, _ = make_student_profile("student")
        self.student.narrative = "Current narrative"
        self.student.save(update_fields=["narrative"])
        self.council = make_user("council", "Council")

    def test_anonymous_redirects_to_login(self):
        response = self.client.get(reverse("VitaEditNarrative"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_student_can_edit_narrative(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse("VitaEditNarrative"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "vita/editnarrative.html")

    def test_non_student_is_redirected_from_edit_narrative(self):
        self.client.force_login(self.council)
        response = self.client.get(reverse("VitaEditNarrative"))
        self.assertRedirects(response, reverse("VitaIndex"), fetch_redirect_response=False)


class VitaOffCampusViewTest(TestCase):
    def setUp(self):
        self.student_user, self.student, self.student_exp = make_student_profile("student")
        self.other_user, self.other_student, self.other_exp = make_student_profile("other_student")
        self.council = make_user("council", "Council")
        self.staff = make_user("staff", "WSP Staff")

    def test_anonymous_redirects_to_login(self):
        response = self.client.get(reverse("VitaOffCampus"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_student_can_view_own_off_campus(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse("VitaOffCampus"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "vita/offcampus.html")

    def test_student_can_save_off_campus_reflection(self):
        self.client.force_login(self.student_user)
        response = self.client.post(
            reverse("VitaOffCampus"),
            {
                "experience_type": OffCampusExperience.INTERNSHIP,
                "completed": OffCampusExperience.Y,
                "reflection": "reflection update",
            },
        )
        self.assertRedirects(response, reverse("VitaOffCampus"), fetch_redirect_response=False)

        self.student_exp.refresh_from_db()
        self.assertEqual(self.student_exp.experience_type, OffCampusExperience.INTERNSHIP)

    def test_student_with_username_argument_redirects_to_own_route(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse("VitaOffCampus") + self.other_user.username)
        self.assertRedirects(response, reverse("VitaOffCampus"), fetch_redirect_response=False)

    def test_council_sees_picker(self):
        self.client.force_login(self.council)
        response = self.client.get(reverse("VitaOffCampus"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "vita/studentpickerform.html")

    def test_council_can_view_student_off_campus_by_username(self):
        self.client.force_login(self.council)
        response = self.client.get(reverse("VitaOffCampus") + self.student_user.username)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "vita/offcampus.html")

    def test_council_picker_post_redirects_to_selected_student(self):
        self.client.force_login(self.council)
        response = self.client.post(reverse("VitaOffCampus"), {"student": self.student_user.id})
        self.assertRedirects(
            response,
            reverse("VitaOffCampus") + self.student_user.username,
            fetch_redirect_response=False,
        )

    def test_council_can_save_notes_for_student(self):
        self.client.force_login(self.council)
        response = self.client.post(
            reverse("VitaOffCampus"),
            {
                "submit": self.student_user.username,
                "approved": OffCampusExperience.Y,
                "council_notes": "approved notes",
            },
        )
        self.assertRedirects(
            response,
            reverse("VitaOffCampus") + self.student_user.username,
            fetch_redirect_response=False,
        )
        self.student_exp.refresh_from_db()
        self.assertEqual(self.student_exp.approved, OffCampusExperience.Y)

    def test_staff_can_view_student_off_campus(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("VitaOffCampus") + self.student_user.username)
        self.assertEqual(response.status_code, 200)

    def test_bad_student_username_redirects_to_index_for_council(self):
        self.client.force_login(self.council)
        response = self.client.get(reverse("VitaOffCampus") + "missing_user")
        self.assertRedirects(response, reverse("VitaIndex"), fetch_redirect_response=False)
