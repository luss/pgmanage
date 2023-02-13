from django.http import JsonResponse, HttpResponse
from app.views.memory_objects import user_authenticated
from app.bgprocess.processes import BatchProcess


@user_authenticated
def index(request):
    process_list = BatchProcess.list(request.user)
    return JsonResponse(data={"data": process_list})


# @blueprint.route('/<pid>', methods=['PUT'], endpoint='acknowledge')
# @login_required


@user_authenticated
def delete_process(request, process_id):
    """
    User has acknowledge the process

    Args:
        process_id:  Process ID

    Returns:
        Positive status
    """
    try:
        BatchProcess.delete(process_id, request.user)
        return HttpResponse(status=204)
    except LookupError as exc:
        return JsonResponse(data={"data": str(exc)}, status=410)


@user_authenticated
def status(request, process_id, out=-1, err=-1):
    try:
        process = BatchProcess(id=process_id)

        return JsonResponse(data={"data": process.status(out, err)})
    except LookupError as exc:
        return JsonResponse(data={"data": str(exc)}, status=410)


@user_authenticated
def stop_process(request, process_id):
    """
    User has stopped the process

    :param process_id: Process ID
    """
    try:
        BatchProcess.stop_process(process_id, request.user)
        return
    except LookupError as exc:
        return JsonResponse(data={"data": str(exc)}, status=410)
