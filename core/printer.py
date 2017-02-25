import os
import sys
import time
import urlparse

if os.name == 'nt':
    RED,MAGENTA,BLUE,GREEN,YELLOW,LBLUE,ENDC = ("","","","","","","")
else:
    RED = '\033[31m'
    MAGENTA = '\033[35m'
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    LBLUE = '\033[36m'
    ENDC = '\033[0m'

COLUMNS = 80
try:
    # (Slightly modified) http://stackoverflow.com/a/943921/91267
    p = os.popen('stty size', 'r')
    rows, columns = p.read().split()
    p.close()
    COLUMNS = int(columns)
    pass
except:
    pass


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
        if task.location:
            target = target + " -> " + task.location
        if len(target) > COLUMNS - 39:
            target = target[:abs(COLUMNS - 39)]
        # If a task is valid means that is should be printed, so a proper
        # linesep will be printed
        linesep = ""
        if task.is_valid():
            linesep = os.linesep
        elif os.name == 'nt':
            return
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
        sys.stdout.write(to_console[:COLUMNS-2] + linesep)
        sys.stdout.flush()
        sys.stdout.write('\r')
        if not os.name == 'nt':
            sys.stdout.write("\x1b[0K")
