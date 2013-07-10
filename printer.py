import os
import sys
import time
import urlparse

from bcolors import BColors

class Console:

    @staticmethod
    def header():
        header = os.linesep + " % | COD |    SIZE    | (line) | time |" \
        + os.linesep + "---------------------------------------" + os.linesep
        sys.stdout.write(header)

    @staticmethod
    def body(task):
        counter = task.number
        percentage = counter * 100 / task.get_payload_length()
        counter += 1
        target = task.target + task.resource + task.extension
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
            color = BColors.GREEN
        if task.response_code == "403":
            color = BColors.RED
        if task.response_code == "301" or task.response_code == "302":
            color = BColors.LBLUE
        if task.response_code == "401":
            color = BColors.RED
        if task.response_code.startswith('5'):
            color = BColors.YELLOW
        if task.content_detected:
            color = BColors.MAGENTA
        to_format = color + "{0: >2} | {1: ^3} | {2: >10} | {3: >6} | {4: >4} | {5}" + BColors.ENDC
        to_console = to_format.format(percentage, task.response_code,
                                    task.response_size, task.number,
                                    int(task.response_time), target)
        sys.stdout.write(to_console + linesep)
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\r')
        sys.stdout.write ("\x1b[0K")
        sys.stdout.flush()
