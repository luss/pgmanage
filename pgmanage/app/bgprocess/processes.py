from abc import abstractmethod
import csv
from datetime import datetime, timedelta
import json
import shutil
from io import StringIO
import os
from pickle import dumps, loads
import sys
import psutil
from subprocess import Popen, PIPE

from app.models.main import Connection, Process
from pgmanage import settings


PROCESS_NOT_STARTED = 0
PROCESS_STARTED = 1
PROCESS_FINISHED = 2
PROCESS_TERMINATED = 3
PROCESS_NOT_FOUND = "Could not find a process with the specified ID."


class IProcessDesc:
    @property
    @abstractmethod
    def message(self):
        pass

    @abstractmethod
    def details(self, cmd, args):
        pass


class BatchProcess:
    def __init__(self, **kwargs):

        self.id = (
            self.desc
        ) = (
            self.cmd
        ) = (
            self.args
        ) = (
            self.log_dir
        ) = self.stdout = self.stderr = self.stime = self.etime = self.ecode = None
        self.env = dict()
        self.user = kwargs.get("user", None)
        if "id" in kwargs:
            self._retrieve_process(kwargs["id"])
        else:
            cmd = kwargs["cmd"]
            # Get system's interpreter
            # if kwargs['cmd'] == 'python':
            #     _cmd = self._get_python_interpreter()

            self._create_process(kwargs["desc"], cmd, kwargs["args"])

    def _retrieve_process(self, _id):
        process = Process.objects.filter(pid=_id, user=self.user).first()

        if process is None:
            raise LookupError(PROCESS_NOT_FOUND)

        try:
            tmp_desc = loads(bytes.fromhex(process.desc))
        except Exception:
            tmp_desc = loads(process.desc)

        # ID
        self.id = _id
        # Description
        self.desc = tmp_desc
        # Status Acknowledged time
        self.atime = process.acknowledge
        # Command
        self.cmd = process.command
        # Arguments
        self.args = process.arguments
        # Log Directory
        self.log_dir = process.logdir
        # Standard ouput log file
        self.stdout = os.path.join(process.logdir, "out")
        # Standard error log file
        self.stderr = os.path.join(process.logdir, "err")
        # Start time
        self.stime = process.start_time
        # End time
        self.etime = process.end_time
        # Exit code
        self.ecode = process.exit_code
        # Process State
        self.process_state = process.process_state
        self.user = process.user

    def _create_process(self, desc, cmd, args):
        ctime = datetime.now().strftime("%Y%m%d%H%M%S%f")

        log_dir = os.path.join(
            os.path.realpath(os.path.expanduser("~/.pgmanage/")), "process_logs"
        )

        def random_number(size):
            import secrets
            import string

            return "".join(
                secrets.choice(string.ascii_uppercase + string.digits)
                for _ in range(size)
            )

        created = False
        size = 0
        uid = ctime
        while not created:
            try:
                uid += random_number(size)
                log_dir = os.path.join(log_dir, uid)
                size += 1
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir, int("700", 8))
                    created = True
            except OSError as oe:
                import errno

                if oe.errno != errno.EEXIST:
                    raise

        # ID
        self.id = ctime
        # Description
        self.desc = desc
        # Status Acknowledged time
        self.atime = None
        # Command
        self.cmd = cmd
        # Log Directory
        self.log_dir = log_dir
        # Standard ouput log file
        self.stdout = os.path.join(log_dir, "out")
        # Standard error log file
        self.stderr = os.path.join(log_dir, "err")
        # Start time
        self.stime = None
        # End time
        self.etime = None
        # Exit code
        self.ecode = None
        # Process State
        self.process_state = PROCESS_NOT_STARTED

        # Arguments
        self.args = args
        args_csv_io = StringIO()
        csv_writer = csv.writer(
            args_csv_io, delimiter=str(","), quoting=csv.QUOTE_MINIMAL
        )
        csv_writer.writerow(args)

        args_val = args_csv_io.getvalue().strip(str("\r\n"))
        tmp_desc = dumps(self.desc).hex()
        connection = Connection.objects.filter(id=desc.sid).first()
        process = Process(
            pid=int(ctime),
            command=cmd,
            arguments=args_val,
            logdir=log_dir,
            desc=tmp_desc,
            user=self.user,
            connection=connection,
        )
        process.save()

    def check_start_end_time(self):
        """
        Check start and end time to check process is still executing or not.
        :return:
        """
        if self.stime is not None:
            if self.etime is None:
                raise RuntimeError("The process has already been started.")
            raise RuntimeError(
                "The process has already finished and cannot be restarted."
            )

    def _get_python_interpreter(self):
        """Get Python Interpreter"""
        if os.name == "nt":
            paths = os.environ["PATH"].split(os.pathsep)

            # current_app.logger.info(
            #     "Process Executor: Operating System Path %s",
            #     str(paths)
            # )

            interpreter = self.get_windows_interpreter(paths)
        else:
            interpreter = sys.executable
            if interpreter.endswith("uwsgi"):
                interpreter = interpreter.split("uwsgi", maxsplit=1)[0] + "python"

        return interpreter if interpreter else "python"

    def start(self, cb=None):
        self.check_start_end_time()

        executor = os.path.join(os.path.dirname(__file__), "process_executor.py")

        interpreter = self._get_python_interpreter()

        cmd = [interpreter, executor, self.cmd]
        cmd.extend(self.args)

        # current_app.logger.info(
        #     "Executing the process executor with the arguments: %s",
        #     str(cmd)
        # )

        env = os.environ.copy()

        env["PROCID"] = self.id
        env["OUTDIR"] = self.log_dir
        env["PGA_BGP_FOREGROUND"] = "1"
        # if config.SERVER_MODE and session and \
        #         session['auth_source_manager']['current_source'] == \
        #         KERBEROS and 'KRB5CCNAME' in session:
        #     env['KRB5CCNAME'] = session['KRB5CCNAME']

        if self.env:
            env.update(self.env)

        # TODO we might not need this
        if cb is not None:
            cb(env)
        if os.name == "nt":
            DETACHED_PROCESS = 0x00000008
            from subprocess import CREATE_NEW_PROCESS_GROUP

            # We need to redirect the standard input, standard output, and
            # standard error to devnull in order to allow it start in detached
            # mode on
            stdout = os.devnull
            stderr = stdout
            stdin = open(os.devnull, "r")
            stdout = open(stdout, "a")
            stderr = open(stderr, "a")

            p = Popen(
                cmd,
                close_fds=False,
                env=env,
                stdout=stdout.fileno(),
                stderr=stderr.fileno(),
                stdin=stdin.fileno(),
                creationflags=(CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS),
            )
        else:
            # if in debug mode, wait for process to complete and
            # get the stdout and stderr of popen.
            # if config.CONSOLE_LOG_LEVEL <= logging.DEBUG:
            #     p = self.get_process_output(cmd, env)
            # else:
            p = Popen(
                cmd,
                close_fds=True,
                stdout=None,
                stderr=None,
                stdin=None,
                start_new_session=True,
                env=env,
            )

        self.ecode = p.poll()

        # Execution completed immediately.
        # Process executor cannot update the status, if it was not able to
        # start properly.
        if self.ecode is not None and self.ecode != 0:
            # There is no way to find out the error message from this process
            # as standard output, and standard error were redirected to
            # devnull.
            p = Process.objects.filter(pid=self.id, user=self.user).first()
            p.start_time = p.end_time = datetime.now().strftime("%Y%m%d%H%M%S%f")
            if not p.exit_code:
                p.exit_code = self.ecode
            p.process_state = PROCESS_FINISHED
            p.save()
        else:
            # Update the process state to "Started"
            p = Process.objects.filter(pid=self.id, user=self.user).first()
            p.process_state = PROCESS_STARTED
            p.save()

    def get_process_output(self, cmd, env):
        """
        :param cmd:
        :param env:
        :return:
        """
        p = Popen(
            cmd,
            close_fds=True,
            stdout=PIPE,
            stderr=PIPE,
            stdin=None,
            start_new_session=True,
            env=env,
        )

        output, errors = p.communicate()
        output = output.decode() if hasattr(output, "decode") else output
        errors = errors.decode() if hasattr(errors, "decode") else errors
        # current_app.logger.debug(
        #     'Process Watcher Out:{0}'.format(output))
        # current_app.logger.debug(
        #     'Process Watcher Err:{0}'.format(errors))

        return p

    def preexec_function(self):
        import signal

        # Detaching from the parent process group
        os.setpgrp()
        # Explicitly ignoring signals in the child process
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    def read_log(self, logfile, log, pos, ctime, ecode=None, enc="utf-8"):
        import re

        completed = True
        idx = 0
        c = re.compile(r"(\d+),(.*$)")

        # If file is not present then
        if not os.path.isfile(logfile):
            return 0, True

        with open(logfile, "rb") as f:
            eofs = os.fstat(f.fileno()).st_size
            f.seek(pos, 0)
            if pos == eofs and ecode is None:
                completed = False

            while pos < eofs:
                idx += 1
                line = f.readline()
                line = line.decode(enc, "replace")
                r = c.split(line)
                if len(r) < 3:
                    # ignore this line
                    pos = f.tell()
                    continue
                if r[1] > ctime:
                    completed = False
                    break
                log.append([r[1], r[2]])
                pos = f.tell()
                if idx >= 1024:
                    completed = False
                    break
                if pos == eofs:
                    if ecode is None:
                        completed = False
                    break

        return pos, completed

    def status(self, out=0, err=0):
        ctime = datetime.now().strftime("%Y%m%d%H%M%S%f")

        stdout = []
        stderr = []
        out_completed = err_completed = False
        process_output = out != -1 and err != -1

        process = Process.objects.filter(pid=self.id, user=self.user).first()
        enc = sys.getdefaultencoding()
        if enc == "ascii":
            enc = "utf-8"

        execution_time = None

        if process is not None:
            status, updated = BatchProcess.update_process_info(process)
            if updated:
                process.save()
            self.stime = process.start_time
            self.etime = process.end_time
            self.ecode = process.exit_code

            if self.stime is not None:
                # stime = parser.parse(self.stime)
                stime = self.stime
                # etime = parser.parse(self.etime or datetime.now().strftime("%Y%m%d%H%M%S%f"))
                etime = self.etime or datetime.now().strftime("%Y%m%d%H%M%S%f")

                execution_time = BatchProcess.total_seconds(etime - stime)

            if process_output:
                out, out_completed = self.read_log(
                    self.stdout, stdout, out, ctime, self.ecode, enc
                )
                err, err_completed = self.read_log(
                    self.stderr, stderr, err, ctime, self.ecode, enc
                )
        else:
            out_completed = err_completed = False

        if out == -1 or err == -1:
            return {
                "start_time": self.stime,
                "exit_code": self.ecode,
                "execution_time": execution_time,
                "process_state": self.process_state,
            }

        return {
            "out": {"pos": out, "lines": stdout, "done": out_completed},
            "err": {"pos": err, "lines": stderr, "done": err_completed},
            "start_time": self.stime,
            "exit_code": self.ecode,
            "execution_time": execution_time,
        }

    @staticmethod
    def _check_start_time(process, data):
        """
        Check start time and its related other timing checks.
        :param p: Process.
        :param data: Data
        :return:
        """
        if "start_time" in data and data.get("start_time", None):
            process.start_time = datetime.strptime(data["start_time"], "%Y%m%d%H%M%S%f")

            # We can't have 'exit_code' without the 'start_time'
            if "exit_code" in data and data.get("exit_code", None) is not None:
                process.exit_code = data["exit_code"]

                # We can't have 'end_time' without the 'exit_code'.
                if "end_time" in data and data.get("end_time", None):
                    process.end_time = datetime.strptime(
                        data["end_time"], "%Y%m%d%H%M%S%f"
                    )

    @staticmethod
    def update_process_info(process):
        if process.start_time is None or process.end_time is None:
            status = os.path.join(process.logdir, "status")
            if not os.path.isfile(status):
                return False, False

            with open(status, "r") as fp:
                import json

                try:
                    data = json.load(fp)

                    #  First - check for the existance of 'start_time'.
                    BatchProcess._check_start_time(process, data)
                    # get the pid of the utility.
                    if "pid" in data:
                        process.utility_pid = data["pid"]

                    return True, True

                except ValueError as e:
                    print("UPDATE_PROCESS_INFO_EXCEPTION")
                    return False, False
        return True, False

    @staticmethod
    def _check_process_desc(p):
        """
        Check process desc instance and return data according to process.
        :param p: process
        :return: return value for details, type_desc and desc related
        to process
        """
        try:
            desc = loads(bytes.fromhex(p.desc))
        except Exception:
            desc = loads(p.desc)

        details = desc
        type_desc = ""
        # current_storage_dir = None

        if isinstance(desc, IProcessDesc):

            args = []
            args_csv = StringIO(
                p.arguments.encode("utf-8")
                if hasattr(p.arguments, "decode")
                else p.arguments
            )
            args_reader = csv.reader(args_csv, delimiter=str(","))
            for arg in args_reader:
                args = args + arg
            details = desc.details(p.command, args)
            type_desc = desc.type_desc
            # if isinstance(desc, (BackupMessage, IEMessage)):
            #     current_storage_dir = desc.current_storage_dir
            desc = desc.message

        # return desc, details, type_desc, current_storage_dir
        return desc, details, type_desc

    @staticmethod
    def list(user):
        processes = Process.objects.filter(user=user)
        changed = False

        # browser_preference = Preferences.module("browser")
        # expiry_add = timedelta(
        #     browser_preference.preference("process_retain_days").get() or 1
        # )
        expiry_add = 1
        res = []
        for p in processes:
            if p.start_time is not None:
                # remove expired jobs
                # process_expiration_time = parser.parse(p.start_time) + expiry_add
                process_expiration_time = p.start_time + timedelta(days=expiry_add)
                if (
                    datetime.now(process_expiration_time.tzinfo)
                    >= process_expiration_time
                ):
                    shutil.rmtree(p.logdir, True)
                    p.delete()
                    changed = True

            status, updated = BatchProcess.update_process_info(p)
            if not status:
                continue
            elif not changed:
                changed = updated

            if p.start_time is None or (
                p.acknowledge is not None and p.end_time is None
            ):
                continue

            # stime = parser.parse(p.start_time)
            stime = p.start_time
            # etime = parser.parse(p.end_time or get_current_time())
            etime = p.end_time or datetime.now().strftime("%Y%m%d%H%M%S%f")
            execution_time = BatchProcess.total_seconds(etime - stime)

            (
                desc,
                details,
                type_desc,
                # current_storage_dir,
            ) = BatchProcess._check_process_desc(p)

            res.append(
                {
                    "id": p.pid,
                    "desc": desc,
                    "type_desc": type_desc,
                    "details": details,
                    "stime": stime,
                    "etime": p.end_time,
                    "exit_code": p.exit_code,
                    "acknowledge": p.acknowledge,
                    "execution_time": execution_time,
                    "process_state": p.process_state,
                    "utility_pid": p.utility_pid,
                    "conn_id": p.connection.id,
                    # "current_storage_dir": current_storage_dir,
                }
            )

        if changed:
            p.save()

        return res

    @staticmethod
    def total_seconds(dt):
        return round(dt.total_seconds(), 2)

    @staticmethod
    def delete(process_id, user):
        """
        Acknowledge from the user, he/she has alredy watched the status.

        Update the acknowledgement status, if the process is still running.
        And, delete the process information from the configuration, and the log
        files related to the process, if it has already been completed.
        """
        process = Process.objects.filter(user=user, pid=process_id).first()

        if process is None:
            raise LookupError(PROCESS_NOT_FOUND)

        if process.end_time is not None:
            logdir = process.logdir

            process.delete()
            import shutil

            shutil.rmtree(logdir, True)
        else:
            process.acknowledge = datetime.now().strftime("%Y%m%d%H%M%S%f")

            process.save()

    # def set_env_variables(self, server, **kwargs):
    #     """Set environment variables"""
    #     if server:
    #         # Set SSL related ENV variables
    #         if (
    #             hasattr(server, "connection_params")
    #             and server.connection_params
    #             and "sslcert" in server.connection_params
    #             and "sslkey" in server.connection_params
    #             and "sslrootcert" in server.connection_params
    #         ):
    #             # SSL environment variables
    #             sslcert = get_complete_file_path(server.connection_params["sslcert"])
    #             sslkey = get_complete_file_path(server.connection_params["sslkey"])
    #             sslrootcert = get_complete_file_path(
    #                 server.connection_params["sslrootcert"]
    #             )

    #             self.env["PGSSLMODE"] = (
    #                 server.connection_params["sslmode"]
    #                 if hasattr(server, "connection_params")
    #                 and "sslmode" in server.connection_params
    #                 else "prefer"
    #             )
    #             self.env["PGSSLCERT"] = "" if sslcert is None else sslcert
    #             self.env["PGSSLKEY"] = "" if sslkey is None else sslkey
    #             self.env["PGSSLROOTCERT"] = "" if sslrootcert is None else sslrootcert

    #         # Set service name related ENV variable
    #         if server.service:
    #             self.env["PGSERVICE"] = server.service

    #     if "env" in kwargs:
    #         self.env.update(kwargs["env"])

    @staticmethod
    def stop_process(process_id, user):
        """ """
        p = Process.objects.filter(user=user, pid=process_id).first()

        if p is None:
            raise LookupError(PROCESS_NOT_FOUND)

        try:
            process = psutil.Process(p.utility_pid)
            process.terminate()
            # Update the process state to "Terminated"
            p.process_state = PROCESS_TERMINATED
        except psutil.NoSuchProcess:
            p.process_state = PROCESS_TERMINATED
        except psutil.Error as e:
            print("ENABLE TO KILL PROCESS")
            # current_app.logger.warning(
            #     _("Unable to kill the background process '{0}'").format(p.utility_pid)
            # )
            # current_app.logger.exception(e)
        # db.session.commit()
        p.save()

    # @staticmethod
    # def update_server_id(_pid, _sid):
    #     p = Process.query.filter_by(user_id=current_user.id, pid=_pid).first()

    #     if p is None:
    #         raise LookupError(PROCESS_NOT_FOUND)

    #     # Update the cloud server id
    #     p.server_id = _sid
    #     db.session.commit()


def escape_dquotes_process_arg(arg):
    # Double quotes has special meaning for shell command line and they are
    # run without the double quotes. Add extra quotes to save our double
    # quotes from stripping.

    dq_id = "#DQ#"

    if arg.startswith('"') and arg.endswith('"'):
        return r"{0}{1}{0}".format(dq_id, arg)
    else:
        return arg
