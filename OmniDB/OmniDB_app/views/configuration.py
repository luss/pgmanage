import json
import ast
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.exceptions import ValidationError
from django.db.models import Q

from OmniDB_app.views.memory_objects import database_required, user_authenticated
from OmniDB_app.utils.conf import get_settings, post_settings
from OmniDB_app.models import ConfigHistory, Connection

@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_configuration(request, v_database):
    json_object = json.loads(request.POST.get('data', None))
    query_filter = json_object.get('query_filter', None)
    settings = get_settings(v_database, query_filter)

    return JsonResponse({'settings': settings})


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_configuration_categories(request, v_database):
    query = v_database.QueryConfigCategories().Rows
    categories = [l.pop() for l in query]
    return JsonResponse({'categories': categories})


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def save_configuration(request, v_database):
    current = get_settings(v_database)
    json_object = json.loads(request.POST.get('data', None))
    update = json_object.get('settings')
    try:
        updated_settings = post_settings(request, v_database, current, update)
        return JsonResponse({'data': updated_settings})
    except ValidationError as e:
        return HttpResponseBadRequest(content=e.message)


@user_authenticated
@database_required(p_check_timeout=True, p_open_connection=True)
def get_configuration_history(request, v_database):
    config_history = ConfigHistory.objects.filter(Q(user=request.user) & \
                                                  Q(connection=Connection.objects.get(id=v_database.v_conn_id))).order_by('-start_time')

    data = []

    for config in config_history:
        data.append({
            "start_time": config.start_time,
            "user": config.user.username,
            "connection": config.connection.id,
            "config_snapshot": config.config_snapshot
        })
    
    return JsonResponse({'config_history': data})
