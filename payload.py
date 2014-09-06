import threading
import Queue
import time

from task import Task

SLEEP_TIME = 0.1


def _populate_list_with_file(file_name):
    """Open a file, read its content and strips it. Returns a list with the content"""
    with open(file_name, 'r') as f:
        tmp_list = f.readlines()
    clean_list = []
    for e in tmp_list:
        e = e.strip()
        clean_list.append(e.decode("utf-8", "replace"))
    return clean_list


class Payload(threading.Thread):
    def __init__(self, target, payload_filename):
        threading.Thread.__init__(self)

        self.target = target
        self.payload_filename = payload_filename
        self.payload = _populate_list_with_file(payload_filename)
        self.queue = Queue.Queue()

        self.extensions = None
        self.length = len(self.payload)
        self.banned_response_codes = None
        self.content = None
        self.remove_slash = False
        self.uppercase = False

    def set_remove_slash(self, remove_slash):
        self.remove_slash = remove_slash

    def set_banned_response_codes(self, banned_response_codes):
        self.banned_response_codes = banned_response_codes

    def set_extensions(self, extensions):
        self.extensions = extensions

    def set_content(self, content):
        self.content = content

    def get_length(self):
        return self.length

    def run(self):
        number = 0

        for resource in self.payload:

            if self.uppercase:
                resource = resource.upper()

            number += 1

            # Skip commented lines
            if resource and resource[0] == '#':
                continue

            # Avoid double // because some dicts have /prepend_words
            if resource and resource[0] == '/':
                resource = resource[1:]

            if self.remove_slash and resource[-1] == '/':
                resource = resource[:-1]

            for extension in self.extensions:
                # If resource is a whole word and user didnt provide a extension
                # put a final /
                if not extension and not '.' in resource and not self.remove_slash:
                    resource += '/'

                # Put a . before extension if the users didnt do it
                if extension and not '.' in extension:
                    extension = '.' + extension

                task = Task(number, self.target, resource, extension)
                task.set_payload_filename(self.payload_filename)
                task.set_payload_length(self.length)
                task.set_banned_response_codes(self.banned_response_codes)
                task.set_content(self.content)
                self.queue.put(task)

        while self.queue and not self.queue.empty():
            time.sleep(SLEEP_TIME)

    def flush(self):
        with self.queue.mutex:
            self.queue = 0

    def set_uppercase(self):
        self.uppercase = True

    @staticmethod
    def _comment(resource):
        """Returns True is the resource starts with a comment sign"""
        for b in ['#']:
            if resource.startswith(b):
                return True
        return False

