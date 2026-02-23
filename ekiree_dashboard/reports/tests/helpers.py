from django.contrib.auth.models import Group, User


def make_user(username, group_name=None, password="testpass"):
    user = User.objects.create_user(username=username, password=password)
    if group_name:
        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)
    return user
