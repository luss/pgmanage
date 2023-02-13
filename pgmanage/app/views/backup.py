import functools
import json
import shutil
import operator
import os

from app.views.memory_objects import database_required_new, user_authenticated

from django.http import JsonResponse

from app.models.main import Connection
from app.bgprocess.processes import BatchProcess, escape_dquotes_process_arg


class BACKUP:
    """
    Constants defined for Backup utilities
    """

    GLOBALS = 1
    SERVER = 2
    OBJECT = 3


class BackupMessage:
    """
    BackupMessage(IProcessDesc)

    Defines the message shown for the backup operation.
    """

    # TODO rename sid(server id) to conn_id
    def __init__(self, backup_type, sid, backup_file, *args, **kwargs):
        self.backup_type = backup_type
        self.sid = sid
        self.bfile = backup_file
        self.database = kwargs["database"] if "database" in kwargs else None
        self.cmd = ""
        self.args_str = "{0} ({1}:{2})"

        # check to we need this?
        def cmd_arg(x):
            if x:
                x = x.replace("\\", "\\\\")
                x = x.replace('"', '\\"')
                x = x.replace('""', '\\"')
                return ' "' + x + '"'
            return ""

        for arg in args:
            if arg and len(arg) >= 2 and arg[:2] == "--":
                self.cmd += " " + arg
            else:
                self.cmd += cmd_arg(arg)

    def get_server_name(self):
        s = Connection.objects.filter(id=self.sid).first()

        if s is None:
            return "Not available"

        # from pgadmin.utils.driver import get_driver
        # driver = get_driver(PG_DEFAULT_DRIVER)
        # manager = driver.connection_manager(self.sid)

        # host = manager.local_bind_host if manager.use_ssh_tunnel else s.host
        # port = manager.local_bind_port if manager.use_ssh_tunnel else s.port

        return "{0} ({1}:{2})".format(s.database, s.server, s.port)

    @property
    def type_desc(self):
        if self.backup_type == BACKUP.OBJECT:
            return "Backing up an object on the server"
        if self.backup_type == BACKUP.GLOBALS:
            return "Backing up the global objects"
        elif self.backup_type == BACKUP.SERVER:
            return "Backing up the server"
        else:
            # It should never reach here.
            return "Unknown Backup"

    @property
    def message(self):
        server_name = self.get_server_name()

        if self.backup_type == BACKUP.OBJECT:
            return f"Backing up an object on the server '{server_name}' from database '{self.database}'"
        if self.backup_type == BACKUP.GLOBALS:
            return f"Backing up the global objects on the server '{server_name}'"
        elif self.backup_type == BACKUP.SERVER:
            return f"Backing up the server '{server_name}'"
        else:
            # It should never reach here.
            return "Unknown Backup"

    # args should be removed
    def details(self, cmd, args):
        server_name = self.get_server_name()
        backup_type = "Backup"
        if self.backup_type == BACKUP.OBJECT:
            backup_type = "Backup Object"
        elif self.backup_type == BACKUP.GLOBALS:
            backup_type = "Backup Globals"
        elif self.backup_type == BACKUP.SERVER:
            backup_type = "Backup Server"

        return {
            "message": self.message,
            "cmd": cmd + self.cmd,
            "server": server_name,
            "object": self.database,
            "type": backup_type,
        }


def get_args_params_values(data, conn, backup_obj_type, backup_file):
    """
    Used internally by create_backup_objects_job. This function will create
    the required args and params for the job.
    :param data: input data
    :param conn: connection obj
    :param backup_obj_type: object type
    :param backup_file: file name
    :return: args array
    """

    host, port = (conn.v_server, str(conn.v_port))
    args = [
        "--file",
        backup_file,
        "--host",
        host,
        "--port",
        port,
        "--username",
        conn.v_user,
        "--no-password",
    ]

    def set_param(key, param, assertion=True):
        if not assertion:
            return
        if data.get(key, None):
            args.append(param)

    def set_value(key, param, default_value=None, assertion=True):
        if not assertion:
            return
        val = data.get(key, default_value)
        if val:
            args.append(param)
            args.append(val)

    if backup_obj_type != "objects":
        args.append("--database")
        args.append(conn.v_service)

    if backup_obj_type == "globals":
        args.append("--globals-only")

    set_param("verbose", "--verbose")
    set_param("dqoute", "--quote-all-identifiers")
    set_value("role", "--role")

    if backup_obj_type == "objects" and data.get("format", None):
        args.extend(
            [
                "--format={0}".format(
                    {"custom": "c", "tar": "t", "plain": "p", "directory": "d"}[
                        data["format"]
                    ]
                )
            ]
        )

        set_param("blobs", "--blobs", data["format"] in ["custom", "tar"])
        set_value("ratio", "--compress", None, ["custom", "plain", "directory"])

    set_param("only_data", "--data-only", data.get("only_data", None))
    set_param(
        "disable_trigger",
        "--disable-triggers",
        data.get("only_data", None) and data.get("format", "") == "plain",
    )

    set_param(
        "only_schema",
        "--schema-only",
        data.get("only_schema", None) and not data.get("only_data", None),
    )

    set_param("dns_owner", "--no-owner")
    set_param("include_create_database", "--create")
    set_param("include_drop_database", "--clean")
    set_param("pre_data", "--section=pre-data")
    set_param("data", "--section=data")
    set_param("post_data", "--section=post-data")
    set_param("dns_privilege", "--no-privileges")
    set_param("dns_tablespace", "--no-tablespaces")
    set_param("dns_unlogged_tbl_data", "--no-unlogged-table-data")
    set_param("use_insert_commands", "--inserts")
    set_param("use_column_inserts", "--column-inserts")
    set_param("disable_quoting", "--disable-dollar-quoting")
    set_param("with_oids", "--oids")
    set_param("use_set_session_auth", "--use-set-session-authorization")

    set_param("no_comments", "--no-comments", int(conn.v_version_num) >= 110000)
    set_param(
        "load_via_partition_root",
        "--load-via-partition-root",
        int(conn.v_version_num) >= 110000,
    )

    set_value("encoding", "--encoding")
    set_value("no_of_jobs", "--jobs")

    # TODO check possibility of backing up few schemas or tables
    args.extend(
        functools.reduce(
            operator.iconcat,
            map(lambda s: ["--schema", s], data.get("schemas", [])),
            [],
        )
    )

    args.extend(
        functools.reduce(
            operator.iconcat, map(lambda t: ["--table", t], data.get("tables", [])), []
        )
    )

    return args


def find(name, path):
    # temporary solution for getting file from system
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


@database_required_new(check_timeout=True, open_connection=True)
@user_authenticated
def create_backup_objects_job(request, database):
    """
    Creates a new job for backup task
    (Backup Database(s)/Schema(s)/Table(s))
    """

    data = json.loads(request.body) if request.body else {}

    data = data.get("data", {})

    backup_obj_type = data.get("type", "objects")

    # TODO find out how to get file name from system path

    backup_file = find(data.get("fileName"), os.path.expanduser("~"))

    # try:
    #     backup_file = filename_with_file_manager_path(
    #         data['file'], (data.get('format', '') != 'directory'))
    # except PermissionError as e:
    #     return unauthorized(errormsg=str(e))
    # except Exception as e:
    #     return bad_request(errormsg=str(e))

    # Fetch the server details like hostname, port, roles etc

    utility = "pg_dump" if backup_obj_type == "objects" else "pg_dumpall"

    ret_val = shutil.which(utility)
    if not ret_val:
        return JsonResponse(data={"data": "Utility file not found"}, status=400)

    args = get_args_params_values(data, database, backup_obj_type, backup_file)

    escaped_args = [escape_dquotes_process_arg(arg) for arg in args]

    try:
        bfile = (
            data["fileName"].encode("utf-8")
            if hasattr(data["fileName"], "encode")
            else data["fileName"]
        )
        if backup_obj_type == "objects":
            args.append(data["database"])
            escaped_args.append(data["database"])
            p = BatchProcess(
                desc=BackupMessage(
                    BACKUP.OBJECT,
                    database.v_conn_id,
                    bfile,
                    *args,
                    database=data["database"],
                ),
                cmd=utility,
                args=escaped_args,
                user=request.user,
            )
        else:
            p = BatchProcess(
                desc=BackupMessage(
                    BACKUP.SERVER if backup_obj_type != "globals" else BACKUP.GLOBALS,
                    database.v_conn_id,
                    bfile,
                    *args,
                ),
                cmd=utility,
                args=escaped_args,
                user=request.user,
            )

        os.environ[str(p.id)] = database.v_password

        # p.set_env_variables(server)

        p.start()
        jid = p.id
    except Exception as exc:
        return JsonResponse(data={"data": str(exc)}, status=410)

    return JsonResponse(data={"job_id": jid, "desc": p.desc.message, "Success": 1})
