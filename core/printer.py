import os
import sys
import time
import urllib.parse as urlparse

if os.name == "nt":
    RED, MAGENTA, BLUE, GREEN, YELLOW, LBLUE, ENDC = ("", "", "", "", "", "", "")
else:
    RED = "\033[31m"
    MAGENTA = "\033[35m"
    BLUE = "\033[34m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    LBLUE = "\033[36m"
    GRAY = "\033[90m"
    ENDC = "\033[0m"
    ESC = chr(27)
    CLEARSCR = "\33[2J"
    CURPOS = "\33[{};{}H"

COLUMNS = 80

banner = """
   _____                _
  / ____|              (_)
 | |     __ _ _ __  ___ _ _ __   __ _
 | |    / _` | '_ \/ __| | '_ \ / _` |
 | |___| (_| | | | \__ \ | | | | (_| |
  \_____\__,_|_| |_|___/_|_| |_|\__,_|

"""


def _get_terminal_width():
    """
        Get the terminal width to adjust columns size
    """
    global COLUMNS
    try:
        # (Slightly modified) http://stackoverflow.com/a/943921/91267
        p = os.popen("stty size", "r")
        rows, columns = p.read().split()
        p.close()
        COLUMNS = int(columns)
    except:
        pass


_get_terminal_width()


class ETAQueue:
    def __init__(self, size, requests, threads):
        self.size = size
        self.times = []
        self.pending_requests = requests
        self.threads = threads

    def get_eta(self):
        mseconds_in_a_hour = 3600000
        mseconds_in_a_minute = 60000
        mseconds_in_a_second = 1000

        median = sum(self.times) // len(self.times)
        mseconds = self.pending_requests * median // self.threads

        (r_hours, hours) = (
            mseconds % mseconds_in_a_hour,
            int(mseconds / mseconds_in_a_hour),
        )
        (r_minutes, minutes) = (
            r_hours % mseconds_in_a_minute,
            int(r_hours / mseconds_in_a_minute),
        )
        (r_seconds, seconds) = (
            r_minutes % mseconds_in_a_second,
            int(r_minutes / mseconds_in_a_second),
        )

        if hours > 99:
            (hours, minutes, seconds) = ("NO", "TE", "ND")

        return "{0:2}h{1:2}m{2:2}s".format(hours, minutes, seconds)

    def set_time(self, time):
        self.pending_requests -= 1
        if len(self.times) == self.size:
            self.times.pop()
        self.times.append(time)


class Console:
    MIN_COLUMN_SIZE = 64
    eta_queue = None
    eta = "00h00m00s"
    show_full_path = False
    show_content_type = False
    visited = {}
    number_of_requests = 0
    number_of_threads = 0
    show_progress = True
    show_colors = True

    @staticmethod
    def banner():
        print(banner)

    @staticmethod
    def curpos(x, y):
        print(CURPOS.format(x, y))

    @staticmethod
    def clear():
        print(CLEARSCR)

    @staticmethod
    def set_show_progress(show_progress):
        Console.show_progress = show_progress

    @staticmethod
    def set_show_colors(show_colors):
        Console.show_colors = show_colors

    @staticmethod
    def start_eta_queue(size):
        Console.eta_queue = ETAQueue(
            size, Console.number_of_requests, Console.number_of_threads
        )

    @staticmethod
    def header():
        header = (
            os.linesep
            + "cod |    size    |  line  | time |"
            + os.linesep
            + "----------------------------------"
            + os.linesep
        )
        sys.stdout.write(header)

    @staticmethod
    def body(task):
        if task.ignorable:
            return
        percentage = int(task.number * 100 / Console.number_of_requests)
        target = task.get_complete_target()
        target = urlparse.urlsplit(target).path

        if task.location:
            target = target + " -> " + task.location

        # If a task is valid means that is should be printed, so a proper
        # linesep will be printed
        linesep = ""
        if task.is_valid():
            linesep = os.linesep
        elif os.name == "nt":
            return

        to_format = (
            "{1: ^3} | {2: >10} | {3: >6} | {4: >4} | {7} [{0: >2}%] - {5: ^9} - {6}"
        )
        to_format_without_progress = (
            "{0: ^3} | {1: >10} | {2: >6} | {3: >4} | {5:^} {4}"
        )

        color = ""
        if Console.show_colors:
            if task.response_code == "200":
                color = GREEN
            if task.response_code == "401" or task.response_code == "403":
                color = RED
            if task.response_code == "404" and (
                not task.response_code in task.banned_response_codes
            ):
                color = GRAY
            if task.response_code == "301" or task.response_code == "302":
                color = LBLUE
            if task.response_code.startswith("5") or task.response_code == "400":
                color = YELLOW
            if task.content_detected:
                color = MAGENTA

            to_format = color + to_format + ENDC
            to_format_without_progress = color + to_format_without_progress + ENDC

        # User wants to see full path
        if Console.show_full_path:
            t_encode = task.get_complete_target()
        else:
            t_encode = target

        # Trying to tame the UNICODE beast on Python
        if not sys.version_info[0] == 3:
            t_encode = t_encode.encode("utf-8")

        # Fix three characters off by one on screen
        if percentage >= 100:
            percentage = 99

        Console.eta_queue.set_time(task.response_time)
        if task.number % 10 == 0:
            Console.eta = Console.eta_queue.get_eta()

        # Show or not 'Content-Type'
        if Console.show_content_type:
            content_type = task.response_type + " |"
        else:
            content_type = ""

        # Skip already visited resources if they does not add value
        if t_encode in Console.visited.keys():
            (code, size) = Console.visited[t_encode]
            if code == task.response_code and size == task.response_size:
                color = None
        else:
            Console.visited[t_encode] = (task.response_code, task.response_size)

        # Cut resource if its length is wider than available columns
        if len(t_encode) > COLUMNS - Console.MIN_COLUMN_SIZE:
            t_encode = t_encode[: abs(COLUMNS - Console.MIN_COLUMN_SIZE)]

        # if an entry is about to be log, remove percentage and eta time
        if color is not None and not task.response_code in task.banned_response_codes:
            to_console = to_format_without_progress.format(
                task.response_code,
                task.response_size,
                task.number,
                int(task.response_time),
                t_encode,
                content_type,
            )

            sys.stdout.write(to_console[: COLUMNS - 2] + os.linesep)
        # print with progress
        elif Console.show_progress:
            to_console = to_format.format(
                percentage,
                task.response_code,
                task.response_size,
                task.number,
                int(task.response_time),
                Console.eta,
                t_encode,
                content_type,
            )

            sys.stdout.write(to_console[: COLUMNS - 2])
            sys.stdout.write("\r")

        sys.stdout.flush()

        if not os.name == "nt" and Console.show_progress:
            sys.stdout.write("\x1b[0K")
