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
ROWS = 70


def _get_terminal_width():
    """
        Get the terminal width to adjust columns size
    """
    try:
        global ROWS
        # (Slightly modified) http://stackoverflow.com/a/943921/91267
        p = os.popen("stty size", "r")
        rows, columns = p.read().split()
        p.close()
        COLUMNS = int(columns)
        ROWS = int(rows)

    except:
        # ʕノ•ᴥ•ʔノ ︵ ┻━┻
        # Assume 80 columns and 70 rows at least
        pass


_get_terminal_width()


class Juicy(OrderedDict):
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        super().move_to_end(key)


class Throughput:
    def __init__(self):
        self.MAX = 10
        self.deltas = []

    def push(self, delta):
        if len(self.deltas) == self.MAX:
            self.deltas.pop(0)

        self.deltas.append(delta)

    def get(self):
        deltas_len = len(self.deltas)
        if deltas_len:
            return round(sum(self.deltas) / deltas_len, 2)
        else:
            return 0.0


class Console:
    config_entries = []
    # fixed_height is a value comming from cansina.py configuration info plus banner
    fixed_height = 10 + 5
    juicy_entries = Juicy()
    last_offset = 0
    number_of_requests = 0
    number_of_threads = 0
    show_colors = True
    show_content_type = False
    show_full_path = False
    show_progress = True
    update_counter = 0
    net_throughput = Throughput()

    @staticmethod
    def curpos(x, y):
        sys.stdout.write(CURPOS.format(y, x))

    @staticmethod
    def clear():
        if Console.show_progress:
            sys.stdout.write(CLEARSCR)

    @staticmethod
    def show_cur():
        if Console.show_progress:
            Console.curpos(0, Console.last_offset)
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
    def add_config(message):
        Console.config_entries.append(f"{message}\n")

    @staticmethod
    def init():
        if Console.show_progress:
            Console.clear()
            Console.hide_cur()

    @staticmethod
    def end():
        if Console.show_progress:
            Console.show_cur()

    @staticmethod
    def banner():
        ascii_banner = """
   ___              _
  / __|__ _ _ _  __(_)_ _  __ _
 | (__/ _` | ' \(_-< | ' \/ _` |
  \___\__,_|_||_/__/_|_||_\__,_|

        """
        sys.stdout.write(ascii_banner)

    @staticmethod
    def config():
        for line in Console.config_entries:
            sys.stdout.write(line)

    @staticmethod
    def progress():
        block = "▇"
        placeholder = "_"
        number_of_blocks = 60
        block_value = 100 / 60

        percentage = Console.update_counter * 100 / Console.number_of_requests
        blocks_to_print = round(percentage / block_value) + 1
        placeholders_to_print = number_of_blocks - blocks_to_print

        sys.stdout.write(
            f"\r{DEL}{Console.update_counter:>{len(str(Console.number_of_requests))}}/{Console.number_of_requests} [{YELLOW}{block*blocks_to_print}{ENDC}{placeholder*placeholders_to_print}] - {round(percentage,1)}%"
        )

    @staticmethod
    def elapsed_time():
        net_throughput = Console.net_throughput.get()
        color = ""

        if Console.show_colors:
            if net_throughput < 553:
                color = GREEN
            elif net_throughput >= 553 and net_throughput < 998:
                color = YELLOW
            elif net_throughput >= 998:
                color = RED

        sys.stdout.write(
            "\r{}{:37} {}{:>} ms{}\n".format(
                DEL, "Thread activity", color, net_throughput, ENDC
            )
        )

    @staticmethod
    def thread_activity(task):
        color = ""
        if Console.show_colors:
            if task.response_code == 200:
                color = GREEN
            if task.response_code == 401 or task.response_code == 403:
                color = RED
            if task.response_code == 404 or (
                task.response_code in task.banned_response_codes
            ):
                color = GRAY
            if task.response_code == 301 or task.response_code == 302:
                color = LBLUE
            if str(task.response_code).startswith("5") or task.response_code == 400:
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
            content_type_color = GRAY if Console.show_colors else ""
            content_type = f"{content_type_color}{task.response_type}{ENDC}"
        else:
            content_type = ""

        # Cut target string if its length is wider than available columns
        if len(target) > COLUMNS:
            target = target[: len(target) - COLUMNS]

        # Format and print info to terminal
        thread_info = f"{color} #{task.thread + 1:<3} {task.response_code}  {target}"
        if Console.show_progress:
            Console.net_throughput.push(task.response_time)
            sys.stdout.write(f"\r{DEL}{thread_info}{ENDC}\n")

        # Add to juicy
        if not task.ignorable:
            size_color = BLUE if Console.show_colors else ""
            formatted_task = f"\r{DEL}{color}{task.response_code:^3}{ENDC} {size_color}{task.response_size:>10} bytes{ENDC} {content_type} {target}"

            if not target in Console.juicy_entries:
                Console.juicy_entries[target] = formatted_task

            if not Console.show_progress:
                formatted_task = f"{color}{task.response_code:^3}{ENDC} {task.response_size:>10} bytes {content_type} {target}\n"
                sys.stdout.write(formatted_task)

    @staticmethod
    def update(task):
        Console.update_counter += 1
        # y-positioning cursor
        # cursor_y = Console.fixed_height
        if Console.show_progress:

            # Show banner
            cursor_y = 0
            Console.curpos(0, cursor_y)
            Console.banner()
            cursor_y += 7

            # Show config
            Console.curpos(0, cursor_y)
            Console.config()
            cursor_y += 9

            # Show thread activity
            cursor_y += 1
            Console.curpos(0, cursor_y)
            Console.elapsed_time()
            cursor_y += 1
            Console.curpos(0, cursor_y + (task.thread + 1))
            Console.thread_activity(task)
            cursor_y += Console.number_of_threads + 1

            # Show progress
            cursor_y += 1
            Console.curpos(0, cursor_y)
            Console.progress()
            cursor_y += 2

            # Show juicy
            juicy_entries = list(Console.juicy_entries.values())
            free_rows = ROWS - cursor_y

            if len(juicy_entries) > free_rows:
                juicy_entries = juicy_entries[len(juicy_entries) - free_rows :]

            for entry in juicy_entries:
                Console.curpos(0, cursor_y)
                cursor_y += 1
                if cursor_y > ROWS:
                    return
                sys.stdout.write(entry)

            Console.last_offset = cursor_y

        else:
            Console.thread_activity(task)

    @staticmethod
    def say(message):
        if Console.show_progress and Console.last_offset < ROWS:
            Console.curpos(0, Console.last_offset)
        sys.stdout.write(f"{message}\n")
