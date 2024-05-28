from app.utils.decorators import superuser_required, user_authenticated
from app.utils.key_manager import key_manager
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.utils import timezone


@superuser_required
@user_authenticated
def get_users(request):
    user_list = []
    user_id_list = []

    try:
        for user in User.objects.all():
            user_data_list = [user.username, "", 1 if user.is_superuser else 0]

            user_list.append(user_data_list)
            user_id_list.append(user.id)
    except Exception as exc:
        return JsonResponse(data={"data": str(exc)}, status=400)

    response_data = {"user_list": user_list, "user_ids": user_id_list}

    return JsonResponse(data=response_data)


@superuser_required
@user_authenticated
def remove_user(request):
    user_id = request.data["id"]

    try:
        user = User.objects.get(id=user_id)
        key_manager.remove(user)
        user.delete()
    except Exception as exc:
        return JsonResponse(data={"data": str(exc)}, status=400)
    return HttpResponse(status=204)


@superuser_required
@user_authenticated
def save_users(request):
    data = request.data

    try:
        changes = data["changes"]

        # Creating new users.
        new_users = changes["new"]
        for user_item in new_users:
            new_user = User.objects.create_user(
                username=user_item[0],
                password=user_item[1],
                email="",
                last_login=timezone.now(),
                is_superuser=True if user_item[2] else False,
                first_name="",
                last_name="",
                is_staff=False,
                is_active=True,
                date_joined=timezone.now(),
            )

        # Editing users.
        edited_users = changes["edited"]
        user_id_list = data["user_id_list"]
        for index, r in enumerate(edited_users):
            user = User.objects.get(id=user_id_list[index])
            user.username = r[0]
            if r[1]:
                user.set_password(r[1])
            user.is_superuser = True if r[2] else False
            user.save()

            if request.user == user and r[1]:
                update_session_auth_hash(request, user)
    except Exception as exc:
        return JsonResponse(data={"data": str(exc)}, status=400)

    return HttpResponse(status=200)
