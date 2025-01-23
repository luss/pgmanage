import os

from app.file_manager.file_manager import FileManager
from app.utils.decorators import user_authenticated
from django.http import FileResponse, HttpResponse, JsonResponse


@user_authenticated
def create(request):
    file_manager = FileManager(request.user)

    data = request.data

    try:
        file_manager.create(data.get("path"), data.get("name"), data.get("type"))
        return JsonResponse({"data": "created"}, status=201)
    except Exception as exc:
        return JsonResponse({"data": str(exc)}, status=400)


@user_authenticated
def get_directory(request):
    file_manager = FileManager(request.user)

    data = request.data
    try:
        if data.get("parent_dir"):
            files = file_manager.get_parent_directory_content(data.get("current_path"))
        else:
            files = file_manager.get_directory_content(data.get("current_path"))
        return JsonResponse(files)
    except Exception as exc:
        return JsonResponse({"data": str(exc)}, status=400)


@user_authenticated
def rename(request):
    file_manager = FileManager(request.user)

    data = request.data

    try:
        file_manager.rename(data.get("path"), data.get("name"))
        return JsonResponse({"data": "success"})
    except Exception as exc:
        return JsonResponse({"data": str(exc)}, status=400)


@user_authenticated
def delete(request):
    file_manager = FileManager(request.user)

    try:
        file_manager.delete(request.data.get("path"))
        return HttpResponse(status=204)
    except Exception as exc:
        return JsonResponse({"data": str(exc)}, status=400)


@user_authenticated
def download(request):
    file_manager = FileManager(request.user)

    data = request.data

    try:
        rel_path = data.get("path")

        if not rel_path:
            return JsonResponse({"data": "File path is required."}, status=400)

        abs_path = file_manager.resolve_path(rel_path)

        file_manager.check_access_permission(abs_path)

        file_manager.assert_exists(abs_path)

        return FileResponse(
            open(abs_path, "rb"),
            as_attachment=True,
            filename=os.path.basename(abs_path),
        )
    except Exception as exc:
        return JsonResponse({"data": str(exc)}, status=400)
