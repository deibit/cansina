import os
import sys
import time
import urlparse

RED = '\033[31m'
MAGENTA = '\033[35m'
BLUE = '\033[34m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
LBLUE = '\033[36m'
ENDC = '\033[0m'


class Console:
    def __init__(self):
        pass

    @staticmethod
    def header():
        header = os.linesep + " % | COD |    SIZE    | (line) | time |" \
            + os.linesep + "---------------------------------------" + os.linesep
        sys.stdout.write(header)

    @staticmethod
    def body(task):
        counter = task.number
        percentage = counter * 100 / task.get_payload_length()
        target = task.get_complete_target()
        target = urlparse.urlsplit(target).path
        if len(target) > 80:
            target = target[:80] + "...(cont)"
        if task.location:
            target = target + " -> " + task.location
        linesep = ""
        if task.is_valid():
            linesep = os.linesep
        color = ""
        if task.response_code == "200":
            color = GREEN
        if task.response_code == "403":
            color = RED
        if task.response_code == "301" or task.response_code == "302":
            color = LBLUE
        if task.response_code == "401":
            color = RED
        if task.response_code.startswith('5'):
            color = YELLOW
        if task.content_detected:
            color = MAGENTA
        to_format = color + "{0: >2} | {1: ^3} | {2: >10} | {3: >6} | {4: >4} | {5}" + ENDC
        to_console = to_format.format(percentage, task.response_code,
                                      task.response_size, task.number,
                                      int(task.response_time), target.encode('utf-8'))
        sys.stdout.write(to_console[:200] + linesep)
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\r')
        sys.stdout.write("\x1b[0K")
