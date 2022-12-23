import json
import ast
from django.http import JsonResponse
from OmniDB_app.views.memory_objects import database_required, user_authenticated


@user_authenticated
@database_required(p_check_timeout = True, p_open_connection = True)
def get_configuration(request, v_database):
    json_object = json.loads(request.POST.get('data', None))
    query_filter = json_object.get('query_filter', None)
    tables_json = v_database.QueryConfiguration(query_filter).Jsonify()
    tables = json.loads(tables_json)
    ret = {}
    for row in tables:
        rows = ret.setdefault(row['category'], [])
        enumvals = row['enumvals']
        if enumvals != '':

            enumvals = list(ast.literal_eval(enumvals))

        rows.append({
            'name': row['name'],
            'setting': row['setting'],
            'setting_raw': row['current_setting'],
            'unit': row['unit'],
            'vartype': row['vartype'],
            'min_val': row['min_val'],
            'max_val': row['max_val'],
            'boot_val': row['boot_val'],
            'reset_val': row['reset_val'],
            'enumvals': enumvals,
            'context': row['context'],
            'desc': row['desc'],
            'pending_restart': row['pending_restart'],
        })

    data = [{'category': k, 'rows': v} for k, v in ret.items()]

    return JsonResponse(data=data, safe=False)


@user_authenticated
@database_required(p_check_timeout = True, p_open_connection = True)
def get_configuration_categories(request, v_database):
    query = v_database.QueryConfigCategories().Rows
    data = [l.pop() for l in query]
    return JsonResponse({'data': data})


# post configurations
@database_required(p_check_timeout = True, p_open_connection = True)
@user_authenticated
def post_configuration(request, database):
    pass

# get configuration status ???????
