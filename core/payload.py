import sys
import threading
import time

try:
    import Queue
except:
    import queue as Queue

from core.task import Task


def _populate_list_with_file(file_name, linenumber):
    """ Open a file, read its content and strips it. Returns a list with the content
        additionally it filter and clean some splinters
    """
    #FIXME: Garbage
    tmp_list = None
    if type(file_name) == list:
        tmp_list = file_name
    else:
        with open(file_name, 'r') as f:
            tmp_list = f.readlines()
            tmp_list = tmp_list[linenumber:]
    clean_list = []
    for e in tmp_list:
        # Delete leading and trailing spaces
        e = e.strip()
        # Skip commented lines in payload files
        if e.startswith('#'):
            continue
        # Remove leading '/' characters
        if e.startswith('/'):
            e = e[1:]

        if sys.version_info[0] == 3:
            e_encode = e
        else:
            e_encode = e.encode('utf-8', 'replace')

        clean_list.append(e)

    return clean_list

def _has_extension(res):
    #whether the last path sector has '.'
    if res.rfind("/") == -1:
        return "." in res
    else:
        return "." in res[res.rfind("/"):]

class Payload():
    def __init__(self, target, payload_filename, resumer):

        self.target = target
        self.payload_filename = payload_filename if not type(payload_filename) == list else "robots.txt"
        self.linenumber = resumer.get_line()
        self.payload = _populate_list_with_file(payload_filename, self.linenumber)
        self.queue = Queue.Queue()
        self.dead = False
        self.extensions = None
        self.length = len(self.payload)
        self.banned_response_codes = None
        self.unbanned_response_codes = None
        self.content = None
        self.remove_slash = False
        self.uppercase = False

    def set_remove_slash(self, remove_slash):
        self.remove_slash = remove_slash

    def set_banned_response_codes(self, banned_response_codes):
        self.banned_response_codes = banned_response_codes

    def set_unbanned_response_codes(self, unbanned_response_codes):
        self.unbanned_response_codes = unbanned_response_codes

    def set_extensions(self, extensions):
        self.extensions = extensions

    def set_content(self, content):
        self.content = content

    def get_length(self):
        return self.length

    def get_total_requests(self):
        return self.length * len(self.extensions)

    def kill(self):
        self.dead = True

    def is_finished(self):
        return self.dead

    def set_uppercase(self, uppercase):
        self.uppercase = uppercase

    def get_queue(self):
        task_id = self.linenumber

        for resource in self.payload:
            if self.uppercase:
                resource = resource.upper()

            task_id += 1

            # Useful when looking for files without extension instead of directories
            if self.remove_slash and resource.endswith("/"):
                resource = resource[:-1]

            for extension in self.extensions:
                # If resource is a whole word and user didnt provide a extension
                # put a final /
                if not extension and not _has_extension(resource) and not self.remove_slash:
                    resource += '/'

                # Put a . before extension if the users didnt do it
                if extension and not '.' in extension:
                    extension = '.' + extension

                task = Task(task_id, self.target, resource, extension)
                task.set_payload_filename(self.payload_filename)
                task.set_payload_length(self.length)
                task.set_banned_response_codes(self.banned_response_codes)
                task.set_unbanned_response_codes(self.unbanned_response_codes)
                task.set_content(self.content)
                self.queue.put(task)

        return self.queue
