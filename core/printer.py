import os
import sys
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
    ENDC = "\033[0m"
    ESC = chr(27)
    GRAY = "\033[38;5;240m"
    CLEARSCR = "\33[2J"
    CURPOS = "\33[{};{}H"
    HIDECUR = "\33[?25l"
    SHOWCUR = "\33[?25h"
    DEL = "\33[2K"

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
    try:
        # (Slightly modified) http://stackoverflow.com/a/943921/91267
        p = os.popen("stty size", "r")
        rows, columns = p.read().split()
        p.close()
        COLUMNS = int(columns)
    except:
        pass


_get_terminal_width()


class Console:
    MIN_COLUMN_SIZE = 64
    show_full_path = False
    show_content_type = False
    visited = {}
    number_of_requests = 0
    number_of_threads = 0
    show_progress = True
    show_colors = True
    # banner height + config height
    fixed_height = 8 + 10
    juicy_counter = 0
    last_offset = 0

    @staticmethod
    def banner():
        sys.stdout.write(banner)

    @staticmethod
    def curpos(x, y):
        sys.stdout.write(CURPOS.format(y, x))

    @staticmethod
    def clear():
        sys.stdout.write(CLEARSCR)

    @staticmethod
    def show_cur():
        Console.curpos(0, Console.last_offset + 5)
        sys.stdout.write(SHOWCUR)

    @staticmethod
    def hide_cur():
        sys.stdout.write(HIDECUR)

    @staticmethod
    def set_show_progress(show_progress):
        Console.show_progress = show_progress

    @staticmethod
    def set_show_colors(show_colors):
        Console.show_colors = show_colors

    @staticmethod
    def header():
        sys.stdout.write("cod |    size    |  line  | time |\n")
        sys.stdout.write("----------------------------------")

    @staticmethod
    def thread_activity(task):

        color = ""
        if Console.show_colors:
            if task.response_code == "200":
                color = GREEN
            if task.response_code == "401" or task.response_code == "403":
                color = RED
            if task.response_code == "404" or (
                task.response_code in task.banned_response_codes
            ):
                color = GRAY
            if task.response_code == "301" or task.response_code == "302":
                color = LBLUE
            if task.response_code.startswith("5") or task.response_code == "400":
                color = YELLOW
            if task.content_detected:
                color = MAGENTA

        target = task.get_complete_target()
        target = urlparse.urlsplit(target).path
        if task.location:
            target = target + " -> " + task.location

        # User wants to see full path
        if Console.show_full_path:
            t_encode = task.get_complete_target()
        else:
            t_encode = target

        if Console.show_content_type:
            content_type = task.response_type + " |"
        else:
            content_type = ""

        # Cut resource if its length is wider than available columns
        if len(target) > COLUMNS:
            target = target[: len(target) - COLUMNS]

        thread_info = f"{color} #{task.thread + 1} | {task.response_code} | {target}"

        sys.stdout.write(f"{DEL}\r{thread_info}{ENDC}")

        if task.is_valid() or task.content_detected:
            Console.juicy_counter += 1
            return f"{color}{task.response_code:^3} | {task.response_size:>10} | {task.number:>6} | {int(task.response_time):>4} | {target}{ENDC}"
        else:
            return None

    @staticmethod
    def progress(count):
        block = "▇"
        placeholder = "_"
        number_of_blocks = 60
        block_value = round(Console.number_of_requests / number_of_blocks)
        blocks_to_print = round(count / block_value)
        placeholders_to_print = number_of_blocks - blocks_to_print
        percentage = int(count * 100 / Console.number_of_requests)

        sys.stdout.write(
            f"\r{count:>{len(str(Console.number_of_requests))}}/{Console.number_of_requests} [{YELLOW}{block*blocks_to_print}{ENDC}{placeholder*placeholders_to_print}] - {percentage}%"
        )

    @staticmethod
    def body(task):
        if task.ignorable:
            return

        cursor_y = Console.fixed_height

        # Show progress
        Console.curpos(0, cursor_y + 1)
        Console.progress(task.number)

        # Show thread activity
        cursor_y += 2  # offset
        Console.curpos(0, cursor_y + task.thread + 1)
        activity = Console.thread_activity(task)
        cursor_y += Console.number_of_threads + 1

        # Header
        cursor_y += 1  # offset
        Console.curpos(0, cursor_y)
        Console.header()
        cursor_y += 1

        # Show juicy
        if activity:
            cursor_y += Console.juicy_counter
            Console.curpos(0, cursor_y)
            sys.stdout.write(activity)

        Console.last_offset = cursor_y

    @staticmethod
    def say(message):
        Console.last_offset += 1
        Console.curpos(0, Console.last_offset)
        sys.stdout.write(message)

    @staticmethod
    def ask(message):
        Console.last_offset += 1
        Console.curpos(0, Console.last_offset)
        sys.stdout.write(message)
        return sys.stdin.read()
