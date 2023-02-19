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

import json
import logging
import os
import signal
import sys
from datetime import datetime
from subprocess import PIPE, Popen
from threading import Thread

_IS_WIN = os.name == "nt"
sys_encoding = None
out_dir = None
log_file = None


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


class ProcessLogger(Thread):
    def __init__(self, stream_type):
        Thread.__init__(self)
        self.process = None
        self.stream = None
        self.logger = open(os.path.join(out_dir, stream_type), "wb", buffering=0)

    def attach_process_stream(self, process, stream):
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
        if self.logger:
            if msg:
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


def update_process_status(**kwargs):
    if out_dir:
        status = dict(
            (k, v)
            for k, v in kwargs.items()
            if k in ("start_time", "end_time", "exit_code", "pid")
        )
        json_status = json.dumps(status)
        logging.info("Updating the status:\n %s", json_status)
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
    logging.exception("Exception occurred")
    if _stderr:
        _stderr.log(str(exc).encode())
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
    command = argv[1:]
    args = dict()

    logging.info("Initialize the rpocess execution: %s", command)

    # Create separate thread for stdout and stderr
    process_stdout = ProcessLogger("out")
    process_stderr = ProcessLogger("err")

    try:
        args.update(
            {
                "start_time": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                "stdout": process_stdout.log,
                "stderr": process_stderr.log,
                "pid": os.getpid(),
            }
        )

        update_process_status(**args)
        logging.info("Status updated.")

        if os.environ.get(os.environ.get("JOB_ID", None), None):
            os.environ["PGPASSWORD"] = os.environ[os.environ["JOB_ID"]]

        kwargs = dict()
        kwargs["close_fds"] = False
        kwargs["shell"] = True if _IS_WIN else False
        kwargs["env"] = os.environ.copy()

        logging.info("Starting the command execution...")
        process = Popen(command, stdout=PIPE, stderr=PIPE, stdin=None, **kwargs)
        args.update(
            {
                "start_time": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                "stdout": process_stdout.log,
                "stderr": process_stderr.log,
                "pid": process.pid,
            }
        )
        update_process_status(**args)
        logging.info("Status updated after starting child process...")

        logging.info("Attaching the loggers to stdout, and stderr...")
        process_stdout.attach_process_stream(process, process.stdout)
        process_stdout.start()
        process_stderr.attach_process_stream(process, process.stderr)
        process_stderr.start()

        process_stdout.join()
        process_stderr.join()

        logging.info("Waiting for the process to finish...")
        exit_code = process.wait()

        if exit_code is None:
            exit_code = process.poll()
        logging.info("Process exited with code: %s", exit_code)
        args.update({"exit_code": exit_code})

        args.update({"end_time": datetime.now().strftime("%Y%m%d%H%M%S%f")})

        _fetch_execute_output(process, process_stdout, process_stderr)

    except OSError as exc:
        _handle_execute_exception(exc, args, process_stderr, exit_code=None)
    except Exception as exc:
        _handle_execute_exception(exc, args, process_stderr, exit_code=-1)
    finally:
        update_process_status(**args)
        logging.info("Exiting the process executor...")
        if process_stderr:
            process_stderr.release()
        if process_stdout:
            process_stdout.release()
        logging.info("Job is finished.")


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
            logging.exception("Exception occured")
    return temp_env


if __name__ == "__main__":

    argv = [unescape_dquotes_process_arg(arg) for arg in sys.argv]

    sys_encoding = sys.getdefaultencoding()
    if not sys_encoding or sys_encoding == "ascii":
        sys_encoding = "utf-8"

    out_dir = os.environ["OUTDIR"]
    log_file = os.path.join(out_dir, ("log_%s" % os.getpid()))

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s  %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
    )

    logging.info("Starting the process executor...")

    # Ignore any signals
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logging.info("Disabled the SIGINT, SIGTERM signals...")

    if _IS_WIN:
        logging.info("Disable the SIGBREAKM signal (windows)...")
        signal.signal(signal.SIGBREAK, signal_handler)

        logging.info("Disabled the SIGBREAKM signal (windows)...")

        logging.info("[CHILD] Start process execution...")
        # This is a child process running as the daemon process.
        # Let's do the job assigning to it.
        try:
            logging.info("Executing the command now from the detached child...")
            execute(argv)
        except Exception:
            logging.exception("Exception occurred")
        # else:
        #     from subprocess import CREATE_NEW_PROCESS_GROUP

        #     DETACHED_PROCESS = 0x00000008

        #     # Forward the standard input, output, and error stream to the
        #     # 'devnull'.
        #     stdin = open(os.devnull, "r")
        #     stdout = open(os.devnull, "a")
        #     stderr = open(os.devnull, "a")
        #     env = os.environ.copy()

        #     # We need environment variables & values in string
        # logging.info("[PARENT] Converting the environment variable in the bytes format...")
        #     try:
        #         env = convert_environment_variables(env)
        #     except Exception:
        #         logging.exception("Exception occurred")

        #     kwargs = {
        #         "stdin": stdin.fileno(),
        #         "stdout": stdout.fileno(),
        #         "stderr": stderr.fileno(),
        #         "creationflags": CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS,
        #         "close_fds": False,
        #         "cwd": out_dir,
        #         "env": env,
        #     }

        #     cmd = [sys.executable]
        #     cmd.extend(argv)

        #     logging.info("[Parent] Command executing %s", cmd)

        #     p = Popen(cmd, **kwargs)

        #     exit_code = p.poll()

        #     if exit_code is not None:
        #         logging.info(f"[PARENT] Child exited with exit-code#{exit_code}...")
        #     else:
        #         logging.info(f"[PARENT] Started the child with PID#{p.pid}")

        #     logging.info("[PARENT] Exiting...")
        #     sys.exit(0)
    else:
        r, w = os.pipe()

        if os.fork() == 0:

            logging.info("[CHILD] Forked the child process...")
            try:
                os.close(r)

                logging.info("[CHILD] Make the child process leader...")
                os.setsid()
                os.umask(0)

                logging.info("[CHILD] Make the child process leader...")
                w = os.fdopen(w, "w")

                logging.info("[CHILD] Inform parent about successful child forking...")
                w.write("1")
                w.close()
                logging.info("[CHILD] Start executing the background process...")
                execute(argv)
            except Exception as error:
                logging.exception("Exception occurred")
                sys.exit(1)
        else:
            os.close(w)
            r = os.fdopen(r)

            r.read()
            logging.info("[PARENT] Got message from the child...")
            r.close()

            logging.info("[PARENT] Exiting...")
            sys.exit(0)
