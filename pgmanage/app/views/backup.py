import functools
import json
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

    def __init__(self, _type, _sid, _bfile, *_args, **_kwargs):
        self.backup_type = _type
        self.sid = _sid
        self.bfile = _bfile
        self.database = _kwargs["database"] if "database" in _kwargs else None
        self.cmd = ""
        self.args_str = "{0} ({1}:{2})"

        def cmd_arg(x):
            if x:
                x = x.replace("\\", "\\\\")
                x = x.replace('"', '\\"')
                x = x.replace('""', '\\"')
                return ' "' + x + '"'
            return ""

        for arg in _args:
            if arg and len(arg) >= 2 and arg[:2] == "--":
                self.cmd += " " + arg
            else:
                self.cmd += cmd_arg(arg)

    def get_server_name(self):
        # s = get_server(self.sid)
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
            return (
                "Backing up an object on the server '{0}' from database '{1}'".format(
                    server_name, self.database
                )
            )
        if self.backup_type == BACKUP.GLOBALS:
            return "Backing up the global objects on the server '{0}'".format(
                server_name
            )
        elif self.backup_type == BACKUP.SERVER:
            return "Backing up the server '{0}'".format(server_name)
        else:
            # It should never reach here.
            return "Unknown Backup"

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


def _get_args_params_values(
    data, conn, backup_obj_type, backup_file, server=None, manager=None
):
    """
    Used internally by create_backup_objects_job. This function will create
    the required args and params for the job.
    :param data: input data
    :param conn: connection obj
    :param backup_obj_type: object type
    :param backup_file: file name
    :param server: server obj
    :param manager: connection manager
    :return: args array
    """
    # from pgadmin.utils.driver import get_driver
    # driver = get_driver(PG_DEFAULT_DRIVER)
    print(conn)

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
        # args.append(server.maintenance_db)

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

    # TODO check how this works
    # args.extend(
    #     functools.reduce(operator.iconcat, map(
    #         lambda s: ['--schema', r'{0}'.format(driver.qtIdent(conn, s).
    #                                              replace('"', '\"'))],
    #         data.get('schemas', [])), []
    #     )
    # )

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

    # args.extend(
    #     functools.reduce(operator.iconcat, map(
    #         lambda t: ['--table',
    #                    r'{0}'.format(driver.qtIdent(conn, t[0], t[1])
    #                                  .replace('"', '\"'))],
    #         data.get('tables', [])), []
    #     )
    # )

    return args


def find(name, path):
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

    data = data["data"]

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

    #  server = get_server(sid)

    # if server is None:
    # return make_json_response(
    #     success=0,
    #     errormsg=_("Could not find the specified server.")
    # )

    # utility = manager.utility('backup') if backup_obj_type == 'objects' \
    # else manager.utility('backup_server')

    utility = "pg_dump" if backup_obj_type == "objects" else "pg_dumpall"

    # TODO use shututils which ot check of utility exists
    import shutil

    ret_val = shutil.which(utility)
    if not ret_val:
        return JsonResponse(data={"data": "Utility file not found"}, status=400)
    # ret_val = does_utility_exist(utility)
    # if ret_val:
    #     return make_json_response(
    #         success=0,
    #         errormsg=ret_val
    #     )

    # args = _get_args_params_values(
    #     data, conn, backup_obj_type, backup_file, server, manager)

    args = _get_args_params_values(data, database, backup_obj_type, backup_file)

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
                    database=data["database"]
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
                    *args
                ),
                cmd=utility,
                args=escaped_args,
                user=request.user,
            )

        # manager.export_password_env(p.id)
        # def export_password_env(self, env):
        # if self.password:
        #     crypt_key_present, crypt_key = get_crypt_key()
        #     if not crypt_key_present:
        #         return False, crypt_key

        #     password = decrypt(self.password, crypt_key).decode()
        #     os.environ[str(env)] = password
        # TODO Is this ok?
        os.environ[str(p.id)] = database.v_password
        # Check for connection timeout and if it is greater than 0 then
        # set the environment variable PGCONNECT_TIMEOUT.
        # timeout = manager.get_connection_param_value('connect_timeout')
        # if timeout and timeout > 0:
        # env = dict()
        # env['PGCONNECT_TIMEOUT'] = str(timeout)
        # p.set_env_variables(server, env=env)
        # else:
        # p.set_env_variables(server)

        p.start()
        jid = p.id
    except Exception as e:
        return JsonResponse(data={"data": str(e)}, status=410)

        # Return response
    return JsonResponse(data={"job_id": jid, "desc": p.desc.message, "Success": 1})
