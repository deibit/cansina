import os
import sys
import urllib.parse as urlparse
from collections import OrderedDict

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
ROWS = 100


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
        ROWS = int(rows)
    except:
        # ʕノ•ᴥ•ʔノ ︵ ┻━┻
        # Assume 80 columns and 100 lines at least
        pass


_get_terminal_width()


class Juicy(OrderedDict):
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        super().move_to_end(key)


class Console:
    show_full_path = False
    show_content_type = False
    number_of_requests = 0
    number_of_threads = 0
    show_progress = True
    show_colors = True
    # fixed_height is a value comming from cansina.py configuration info plus banner
    fixed_height = 10 + 5
    juicy_entries = Juicy()
    last_offset = 0
    config_entries = []

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
        # print(Console.juicy_entries.keys())

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
    def add_config(message):
        Console.config_entries.append(f"{message}\n")

    @staticmethod
    def banner():
        offset = 5
        ascii_banner = """
   ___              _
  / __|__ _ _ _  __(_)_ _  __ _
 | (__/ _` | ' \(_-< | ' \/ _` |
  \___\__,_|_||_/__/_|_||_\__,_|

        """
        sys.stdout.write(ascii_banner)
        return offset

    @staticmethod
    def config():
        offset = 0
        for line in Console.config_entries:
            offset += 1
            sys.stdout.write(line)
        return offset

    @staticmethod
    def progress(count):
        offset = 1
        block = "▇"
        placeholder = "_"
        number_of_blocks = 60
        block_value = 100 / 60

        percentage = count * 100 / Console.number_of_requests
        blocks_to_print = round(percentage / block_value) + 1
        placeholders_to_print = number_of_blocks - blocks_to_print

        sys.stdout.write(
            f"\r{count:>{len(str(Console.number_of_requests))}}/{Console.number_of_requests} [{YELLOW}{block*blocks_to_print}{ENDC}{placeholder*placeholders_to_print}] - {round(percentage,1)}%"
        )

        return offset

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

        # Full path
        if Console.show_full_path:
            target = task.get_complete_target()

        # Content type
        if Console.show_content_type:
            content_type = task.response_type + " |"
        else:
            content_type = ""

        # Cut target string if its length is wider than available columns
        if len(target) > COLUMNS:
            target = target[: len(target) - COLUMNS]

        # Format and print info to terminal
        thread_info = f"{color} #{task.thread + 1:<3} | {task.response_code} | {target}"
        sys.stdout.write(f"\r{DEL}{thread_info}{ENDC}")

        # Add to juicy
        if task.is_valid() or task.content_detected:
            formatted_task = f"\r{DEL}{color}{task.response_code:^3} | {task.response_size:>10} | {task.number:>6} | {int(task.response_time):>4} | {target}{ENDC}"
            if not target in Console.juicy_entries:
                Console.juicy_entries[target] = formatted_task

    @staticmethod
    def header():
        offset = 5
        sys.stdout.write("Results\n")
        sys.stdout.write("\n")
        sys.stdout.write("----------------------------------\n")
        sys.stdout.write("Cod |    Size    |  Line  | Time |\n")
        sys.stdout.write("----------------------------------")
        return offset

    @staticmethod
    def body(task):
        # y-positioning cursor
        # cursor_y = Console.fixed_height
        cursor_y = 0
        Console.curpos(0, cursor_y)
        cursor_y += Console.banner()

        # Show banner
        cursor_y += 2
        Console.curpos(0, cursor_y)
        cursor_y += Console.config()

        # Show progress
        cursor_y += 1
        Console.curpos(0, cursor_y)
        cursor_y += Console.progress(task.number)
        cursor_y += 1

        # Show thread activity
        Console.curpos(0, cursor_y)
        sys.stdout.write("Thread activity")
        cursor_y += 1
        Console.curpos(0, cursor_y + (task.thread + 1))
        Console.thread_activity(task)
        cursor_y += Console.number_of_threads + 1

        # Header
        cursor_y += 1  # offset
        Console.curpos(0, cursor_y)
        cursor_y += Console.header()

        # Show juicy
        juicy_entries = list(Console.juicy_entries.values())
        start_from = 0
        stop_in = len(juicy_entries) - 1
        free_rows = ROWS - cursor_y

        if len(juicy_entries) > free_rows:
            start_from = len(juicy_entries) - free_rows
            stop_in = free_rows

        for y, entry in enumerate(juicy_entries[start_from:stop_in]):
            Console.curpos(0, cursor_y)
            cursor_y += 1
            if cursor_y > ROWS:
                return
            sys.stdout.write(entry)

        Console.last_offset = cursor_y

    @staticmethod
    def say(message):
        Console.curpos(0, Console.last_offset)
        sys.stdout.write(f"{message}\n")
