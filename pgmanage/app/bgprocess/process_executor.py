"""
This python script is responsible for executing a process, and logs its output,
and error in the given output directory.

We will create a detached process, which executes this script.

This script will:
* Fetch the configuration from the given database.
* Run the given executable specified in the configuration with the arguments.
* Create log files for both stdout, and stdout.
* Update the start time, end time, exit code, etc in the configuration
  database.

Args:
  list of program and arguments passed to it.

It also depends on the following environment variable for proper execution.
PROCID - Process-id
OUTDIR - Output directory
"""

# To make print function compatible with python2 & python3
import sys
import os
from datetime import datetime, timedelta
from subprocess import Popen, PIPE
from threading import Thread
import signal
from django.utils.timezone import make_aware

_IS_WIN = os.name == "nt"
_ZERO = timedelta(0)
sys_encoding = None
fs_encoding = None
out_dir = None
log_file = None


def log(msg):
    with open(log_file, "a") as fp:
        fp.write(("INFO:: %s\n" % msg.encode("ascii", "xmlcharrefreplace")))


def unescape_dquotes_process_arg(arg):
    # Double quotes has special meaning for shell command line and they are
    # run without the double quotes.
    #
    # Remove the saviour #DQ#

    # This cannot be at common place as this file executes
    # separately from pgadmin
    dq_id = "#DQ#"

    if arg.startswith(dq_id) and arg.endswith(dq_id):
        return "{0}".format(arg[len(dq_id) : -len(dq_id)])
    else:
        return arg


def log_exception():
    type_, value_, traceback_ = sys.exc_info()

    with open(log_file, "a") as fp:
        from traceback import format_exception

        res = "".join(format_exception(type_, value_, traceback_))

        fp.write(f"EXCEPTION::\n{res}")
        return res


# Copied the 'UTC' class from the 'pytz' package to allow to run this script
# without any external dependent library, and can be used with any python
# version.
# class UTC(tzinfo):
#     """UTC

#     Optimized UTC implementation. It unpickles using the single module global
#     instance defined beneath this class declaration.
#     """
#     zone = "UTC"

#     _utcoffset = _ZERO
#     _dst = _ZERO
#     _tzname = zone

#     def fromutc(self, dt):
#         if dt.tzinfo is None:
#             return self.localize(dt)
#         return super(UTC.__class__, self).fromutc(dt)

#     def utcoffset(self, dt):
#         return _ZERO

#     def tzname(self, dt):
#         return "UTC"

#     def dst(self, dt):
#         return _ZERO

#     def localize(self, dt):
#         """Convert naive time to local time"""
#         if dt.tzinfo is not None:
#             raise ValueError('Not naive datetime (tzinfo is already set)')
#         return dt.replace(tzinfo=self)

#     def normalize(self, dt):
#         """Correct the timezone information on the given datetime"""
#         if dt.tzinfo is self:
#             return dt
#         if dt.tzinfo is None:
#             raise ValueError('Naive time - no tzinfo set')
#         return dt.astimezone(self)

#     def __repr__(self):
#         return "<UTC>"

#     def __str__(self):
#         return "UTC"


# def get_current_time(format='%Y-%m-%d %H:%M:%S.%f %z'):
#     return datetime.utcnow().replace(
#         tzinfo=UTC()
#     ).strftime(format)


class ProcessLogger(Thread):
    """
    This class definition is responsible for capturing & logging
    stdout & stderr messages from subprocess

    Methods:
    --------
    * __init__(stream_type)
     - This method is use to initlize the ProcessLogger class object

    * log(msg)
     - Log message in the orderly manner.

    * run()
     - Reads the stdout/stderr for messages and sent them to logger
    """

    def __init__(self, stream_type):
        """
        This method is use to initialize the ProcessLogger class object

        Args:
            stream_type: Type of STD (std)

        Returns:
            None
        """

        Thread.__init__(self)
        self.process = None
        self.stream = None
        self.logger = open(os.path.join(out_dir, stream_type), "wb", buffering=0)

    def attach_process_stream(self, process, stream):
        """
        This function will attach a process and its stream with this thread.

        Args:
            process: Process
            stream: Stream attached with the process

        Returns:
            None
        """
        self.process = process
        self.stream = stream

    def log(self, msg):
        """
        This function will update log file

        Args:
            msg: message

        Returns:
            None
        """
        # Write into log file
        if self.logger:
            if msg:
                # self.logger.write(
                #     get_current_time(
                #         format='%y%m%d%H%M%S%f'
                #     ).encode('utf-8')
                # )
                self.logger.write(
                    datetime.now().strftime("%Y%m%d%H%M%S%f").encode("utf-8")
                )
                self.logger.write(b",")
                self.logger.write(msg.lstrip(b"\r\n" if _IS_WIN else b"\n"))
                self.logger.write(os.linesep.encode("utf-8"))

            return True
        return False

    def run(self):
        if self.process and self.stream:
            while True:
                nextline = self.stream.readline()

                if nextline:
                    self.log(nextline)
                else:
                    if self.process.poll() is not None:
                        break

    def release(self):
        if self.logger:
            self.logger.close()
            self.logger = None


def update_status(**kwargs):
    """
    This function will updates process stats

    Args:
        kwargs - Process configuration details

    Returns:
        None
    """
    import json

    if out_dir:
        status = dict(
            (k, v)
            for k, v in kwargs.items()
            if k in ("start_time", "end_time", "exit_code", "pid")
        )
        json_status = json.dumps(status)
        log(f"Updating the status:\n{json_status}")
        with open(os.path.join(out_dir, "status"), "w") as fp:
            json.dump(status, fp)
    else:
        raise ValueError("Please verify pid and db_file arguments.")


def _handle_execute_exception(exc, args, _stderr, exit_code=None):
    """
    Used internally by execute to handle exception
    :param ex: exception object
    :param args: execute args dict
    :param _stderr: stderr
    :param exit_code: exit code override
    """
    info = log_exception()
    if _stderr:
        _stderr.log(info)
    else:
        print(f"WARNING: {str(exc)}")
    args.update({"end_time": datetime.now().strftime("%Y%m%d%H%M%S%f")})
    args.update({"exit_code": exc.errno if exit_code is None else exit_code})


def _fetch_execute_output(process, _stdout, _stderr):
    """
    Used internally by execute to fetch execute output and log it.
    :param process: process obj
    :param _stdout: stdout
    :param _stderr: stderr
    """
    data = process.communicate()
    if data:
        if data[0]:
            _stdout.log(data[0])
        if data[1]:
            _stderr.log(data[1])


def execute(argv):
    """
    This function will execute the background process

    Returns:
        None
    """
    # TODO  check what do we get here
    command = argv[1:]
    args = dict()
    log(f"Initialize the process execution: {command}")

    # Create separate thread for stdout and stderr
    process_stdout = ProcessLogger("out")
    process_stderr = ProcessLogger("err")

    try:
        # update start_time
        args.update(
            {
                # "start_time": make_aware(datetime.now()).strftime("%Y%m%d%H%M%S%f"),
                "start_time": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                "stdout": process_stdout.log,
                "stderr": process_stderr.log,
                "pid": os.getpid(),
            }
        )

        # Update start time
        update_status(**args)
        log("Status updated...")

        if os.environ.get(os.environ.get("PROCID", None), None):
            os.environ["PGPASSWORD"] = os.environ[os.environ["PROCID"]]

        kwargs = dict()
        kwargs["close_fds"] = False
        kwargs["shell"] = True if _IS_WIN else False

        # We need environment variables & values in string
        kwargs["env"] = os.environ.copy()

        log("Starting the command execution...")
        process = Popen(command, stdout=PIPE, stderr=PIPE, stdin=None, **kwargs)
        args.update(
            {
                # "start_time": make_aware(datetime.now()).strftime("%Y%m%d%H%M%S%f"),
                "start_time": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                "stdout": process_stdout.log,
                "stderr": process_stderr.log,
                "pid": process.pid,
            }
        )
        update_status(**args)
        log("Status updated after starting child process...")

        log("Attaching the loggers to stdout, and stderr...")
        # Attach the stream to the process logger, and start logging.
        process_stdout.attach_process_stream(process, process.stdout)
        process_stdout.start()
        process_stderr.attach_process_stream(process, process.stderr)
        process_stderr.start()

        # Join both threads together
        process_stdout.join()
        process_stderr.join()

        log("Waiting for the process to finish...")
        # Child process return code
        exit_code = process.wait()

        if exit_code is None:
            exit_code = process.poll()

        log("Process exited with code: {0}".format(exit_code))
        args.update({"exit_code": exit_code})

        # Add end_time
        # args.update({"end_time": make_aware(datetime.now()).strftime("%Y%m%d%H%M%S%f")})
        args.update({"end_time": datetime.now().strftime("%Y%m%d%H%M%S%f")})

        # Fetch last output, and error from process if it has missed.
        _fetch_execute_output(process, process_stdout, process_stderr)

    # If executable not found or invalid arguments passed
    except OSError as exc:
        _handle_execute_exception(exc, args, process_stderr, exit_code=None)
    # Unknown errors
    except Exception as exc:
        _handle_execute_exception(exc, args, process_stderr, exit_code=-1)
    finally:
        # Update the execution end_time, and exit-code.
        update_status(**args)
        log("Exiting the process executor...")
        if process_stderr:
            process_stderr.release()
        if process_stdout:
            process_stdout.release()
        log("Bye!")


def signal_handler(signal, msg):
    # Let's ignore all the signal comming to us.
    pass


def convert_environment_variables(env):
    """
    This function is use to convert environment variable to string
    because environment variable must be string in popen
    :param env: Dict of environment variable
    :return: Encoded environment variable as string
    """
    temp_env = dict()
    for key, value in env.items():
        try:
            if not isinstance(key, str):
                key = key.encode(sys_encoding)
            if not isinstance(value, str):
                value = value.encode(sys_encoding)
            temp_env[key] = value
        except Exception:
            log_exception()
    return temp_env


if __name__ == "__main__":

    argv = [unescape_dquotes_process_arg(arg) for arg in sys.argv]

    sys_encoding = sys.getdefaultencoding()
    if not sys_encoding or sys_encoding == "ascii":
        # Fall back to 'utf-8', if we couldn't determine the default encoding,
        # or 'ascii'.
        sys_encoding = "utf-8"

    fs_encoding = sys.getfilesystemencoding()
    if not fs_encoding or fs_encoding == "ascii":
        # Fall back to 'utf-8', if we couldn't determine the file-system
        # encoding or 'ascii'.
        fs_encoding = "utf-8"

    out_dir = os.environ["OUTDIR"]
    log_file = os.path.join(out_dir, ("log_%s" % os.getpid()))

    log("Starting the process executor...")

    # Ignore any signals
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    log("Disabled the SIGINT, SIGTERM signals...")

    if _IS_WIN:
        log("Disable the SIGBREAKM signal (windows)...")
        signal.signal(signal.SIGBREAK, signal_handler)
        log("Disabled the SIGBREAKM signal (windows)...")

        # For windows:
        # We would run the process_executor in the detached mode again to make
        # the child process to run as a daemon. And, it would run without
        # depending on the status of the web-server.
        if (
            "PGA_BGP_FOREGROUND" in os.environ
            and os.environ["PGA_BGP_FOREGROUND"] == "1"
        ):
            log("[CHILD] Start process execution...")
            # This is a child process running as the daemon process.
            # Let's do the job assigning to it.
            try:
                log("Executing the command now from the detached child...")
                execute(argv)
            except Exception:
                print("EXCEPTION")
                # _log_exception()
        else:
            from subprocess import CREATE_NEW_PROCESS_GROUP

            DETACHED_PROCESS = 0x00000008

            # Forward the standard input, output, and error stream to the
            # 'devnull'.
            stdin = open(os.devnull, "r")
            stdout = open(os.devnull, "a")
            stderr = open(os.devnull, "a")
            env = os.environ.copy()
            env["PGA_BGP_FOREGROUND"] = "1"

            # We need environment variables & values in string
            log("[PARENT] Converting the environment variable in the bytes format...")
            try:
                env = convert_environment_variables(env)
            except Exception:
                log_exception()

            kwargs = {
                "stdin": stdin.fileno(),
                "stdout": stdout.fileno(),
                "stderr": stderr.fileno(),
                "creationflags": CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS,
                "close_fds": False,
                "cwd": out_dir,
                "env": env,
            }

            cmd = [sys.executable]
            cmd.extend(argv)

            log(f"[PARENT] Command executings: {cmd}")

            p = Popen(cmd, **kwargs)

            exit_code = p.poll()

            if exit_code is not None:
                log(f"[PARENT] Child exited with exit-code#{exit_code}...")
            else:
                log(f"[PARENT] Started the child with PID#{p.pid}")

            # Question: Should we wait for sometime?
            # Answer: Looks the case...
            from time import sleep

            sleep(2)
            log("[PARENT] Exiting...")
            sys.exit(0)
    else:
        r, w = os.pipe()

        # For POSIX:
        # We will fork the process, and run the child process as daemon, and
        # let it do the job.
        if os.fork() == 0:
            log("[CHILD] Forked the child process...")
            try:
                os.close(r)

                log("[CHILD] Make the child process leader...")
                os.setsid()
                os.umask(0)

                log("[CHILD] Make the child process leader...")
                w = os.fdopen(w, "w")

                log("[CHILD] Inform parent about successful child forking...")
                w.write("1")
                w.close()

                log("[CHILD] Start executing the background process...")
                execute(argv)
            except Exception:
                log_exception()
                sys.exit(1)
        else:
            os.close(w)
            r = os.fdopen(r)

            r.read()
            log("[PARENT] Got message from the child...")
            r.close()

            log("[PARENT] Exiting...")
            sys.exit(0)
