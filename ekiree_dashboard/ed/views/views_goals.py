import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from ed.forms import EducationalGoalForm
from ed.tools import EducationalGoal
from siteconfig.models import get_hero_image

logger = logging.getLogger(__name__)


@login_required
def DeleteEducationalGoal(request):
    if request.method == "POST":
        try:
            delobj = EducationalGoal.objects.get(
                student=request.user,
                id=request.POST.get("egoal_id"),
            )
            delobj.delete()
            return HttpResponseRedirect(reverse("AddGoal"))

        except EducationalGoal.DoesNotExist:
            return HttpResponseRedirect(reverse("Index"))
    else:
        return HttpResponseRedirect(reverse("Index"))


@login_required
def Goals(request):
    user = request.user
    edgoals = EducationalGoal.objects.filter(student=user)

    if request.method == "GET":
        return render(
            request,
            "ed/allgoals.html",
            {
                "edgoals": edgoals,
                "pagename": "Your Educational Goals",
                "hero": get_hero_image("ed"),
            },
        )
    else:
        return HttpResponseRedirect(reverse("Index"))


@login_required
def AddEducationalGoal(request):
    user = request.user
    form = EducationalGoalForm(user=user)

    if request.method == "GET":
        edgoals = EducationalGoal.objects.filter(student=user)

        return render(
            request,
            "ed/EducationalGoalForm.html",
            {
                "edgoals": edgoals,
                "pagename": "Your Educational Goals",
                "form": form,
                "hero": get_hero_image("ed"),
            },
        )

    elif request.method == "POST":
        form = EducationalGoalForm(request.POST, user=user)

        if form.is_valid():
            goal = form.save(commit=False)
            goal.student = request.user
            goal.save()
            goal.courses.set(form.cleaned_data.get("courses"))
            form.save_m2m()

        return HttpResponseRedirect(reverse("AddGoal"))

    else:
        return HttpResponseRedirect(reverse("Index"))


@login_required
def EditEDGoal(request, goal_id=None):
    user = request.user
    edgoal = EducationalGoal.objects.get(id=goal_id)
    if (request.method == "GET") and (user == edgoal.student):
        form = EducationalGoalForm(user=user)
        form.fields["title"].initial = edgoal.title
        form.fields["description"].initial = edgoal.description

        course_id = []
        for course in edgoal.courses.all():
            course_id.append(course.id)
        form.fields["courses"].initial = course_id

        return render(
            request,
            "ed/editgoal.html",
            {
                "edgoal": edgoal,
                "form": form,
                "pagename": "Edit Goal",
                "hero": get_hero_image("ed"),
            },
        )
    elif (request.method == "POST") and (user == edgoal.student):
        form = EducationalGoalForm(
            request.POST or None,
            instance=edgoal,
            user=user,
        )
        if form.is_valid:
            form.save()
            return HttpResponseRedirect(reverse("AllGoals"))

        else:
            return HttpResponseRedirect(reverse("EDIndex"))
    else:
        return HttpResponseRedirect(reverse("EDIndex"))
