import json
from django.http import (
    JsonResponse,
    HttpResponseBadRequest,
    HttpResponseServerError,
    HttpResponseForbidden,
    HttpResponse,
)
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from django.db.models import Q
from django.views.decorators.http import require_http_methods

from OmniDB_app.models import ConfigHistory, Connection
from OmniDB_app.views.memory_objects import database_required, user_authenticated
from OmniDB_app.utils.conf import get_settings, post_settings, get_settings_status


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_configuration(request, v_database):
    json_object = json.loads(request.POST.get("data", None))
    query_filter = json_object.get("query_filter", None)
    settings = get_settings(v_database, query_filter)

    return JsonResponse({"settings": settings})


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_configuration_categories(request, v_database):
    query = v_database.QueryConfigCategories().Rows
    categories = [l.pop() for l in query]
    return JsonResponse({"categories": categories})


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def save_configuration(request, v_database):
    json_object = json.loads(request.POST.get("data", None))
    update = json_object.get("settings")
    commit_comment = json_object.get("commit_comment")
    new_config = json_object.get("new_config") == True
    try:
        updated_settings = post_settings(
            request, v_database, update, commit_comment, new_config
        )
        return JsonResponse(data=updated_settings)
    except ValidationError as e:
        return HttpResponseBadRequest(content=e.message)
    except DatabaseError as e:
        return HttpResponseServerError(content=e)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_configuration_history(request, v_database):
    config_history = ConfigHistory.objects.filter(
        Q(user=request.user)
        & Q(connection=Connection.objects.get(id=v_database.v_conn_id))
    ).order_by("-start_time")

    data = []

    for config in config_history:
        data.append(
            {
                "id": config.id,
                "start_time": config.start_time,
                "user": config.user.username,
                "connection": config.connection.id,
                "config_snapshot": json.loads(config.config_snapshot),
                "commit_comment": config.commit_comment,
            }
        )

    return JsonResponse({"config_history": data})


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_status(request, v_database):
    settings_status = get_settings_status(v_database)
    return JsonResponse(settings_status)


@require_http_methods(["DELETE"])
@user_authenticated
def delete_config(request, config_id):
    config = ConfigHistory.objects.filter(id=config_id).first()

    if config:
        if config.user.id != request.user.id:
            return HttpResponseForbidden(
                content="You are not allowed to delete not yours configurations."
            )

        config.delete()
    return HttpResponse(status=204)
