import sys
import threading
import time
import fileinput
import os
import os.path
import fnmatch
import queue

import urllib.parse as urlparse

from core.task import Task


def _get_url_components(target):
    """ Get a url and returns multiple paths composed by recursive components"""
    path = [i for i in urlparse.urlparse(target).path.split("/") if len(i) > 0]
    temp_path = ""
    list_path = ["/"]
    for component in path:
        sub = "/%s" % component
        temp_path += sub
        list_path.append(temp_path + "/")
    return list_path


def _populate_list_with_file(file_name, linenumber):
    """ Open a file, read its content and strips it. Returns a list with the content
        additionally it filter and clean some splinters
    """

    def _read_a_file_return_a_list(file_name):
        """
            Small utility function. Open a file a return its content as a list
        """
        tmp_list = []
        try:
            if sys.version_info > (3, 0):
                f = open(file_name, "r", encoding="latin-1")
            else:
                f = open(file_name, "r")
            tmp_list = f.readlines()

        except (OSError, IOError) as e:
            print(
                "[!] Opening payload. Check file, list of files or directory content."
            )
            print(e)
            sys.exit()

        return tmp_list

    # FIXME: Garbage
    tmp_list = None
    # If we receive a list then they are robots.txt entries
    if type(file_name) == list:
        tmp_list = file_name
    # If filename is - we are dealing with stdin
    elif file_name == "-":
        tmp_list = []
        for line in fileinput.input(files=file_name):
            tmp_list.append(line)
    # Single file, could be a list of lists or a single payload
    elif os.path.isfile(file_name):
        tmp_list = _read_a_file_return_a_list(file_name)
        # Now is time to check if is a list or single payload
        if not file_name.endswith(".payload"):
            tmp_list = tmp_list[linenumber:]
        else:
            payload_list = tmp_list
            tmp_list = []
            print("[*] Trying to load {0} files as payloads".format(len(payload_list)))
            for item in payload_list:
                tmp_list.extend(_read_a_file_return_a_list(item.strip()))

    # If we receive a dir then try to open all .txt files in there
    elif os.path.isdir(file_name):
        tmp_list = []
        print(
            "[*] Directory payload inclusion. All *.txt will be treated as a payload."
        )
        for file in os.listdir(file_name):
            if fnmatch.fnmatch(file, "*.txt"):
                tmp_list.extend(
                    _read_a_file_return_a_list("{0}/{1}".format(file_name, file))
                )

    clean_list = []
    for e in tmp_list:
        # Delete leading and trailing spaces
        e = e.strip()
        # Skip commented lines in payload files
        if e.startswith("#"):
            continue
        # Remove leading '/' characters
        if e.startswith("/"):
            e = e[1:]

        if sys.version_info[0] == 3:
            e_encode = e
        else:
            e_encode = e.decode("utf-8", "replace")
        clean_list.append(e_encode)
    return clean_list


def _has_extension(res):
    # whether the last path sector has '.'
    if res.rfind("/") == -1:
        return "." in res
    else:
        return "." in res[res.rfind("/") :]


class Payload:
    def __init__(self, target, payload_filename, resumer):

        self.target = target
        self.task_id = 0
        # Payload may be a filename, a python list, a directory or a file with
        # paths to multiple payload files
        self.payload_filename = (
            payload_filename if not type(payload_filename) == list else "robots.txt"
        )
        self.linenumber = resumer.get_line()
        self.payload = _populate_list_with_file(payload_filename, self.linenumber)
        self.queue = queue.Queue()
        self.dead = False
        self.extensions = None
        self.banned_response_codes = None
        self.unbanned_response_codes = None
        self.content = None
        self.remove_slash = False
        self.uppercase = False
        self.capitalize = False
        self.recursive = False
        self.strip_extension = False
        self.only_alpha = False
        self.total_requests = 0
        self.number_of_tasks = 0

    def get_total_requests(self):
        return self.number_of_tasks

    def set_recursive(self, recursion):
        self.recursive = recursion

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

    def kill(self):
        self.dead = True

    def is_finished(self):
        return self.dead

    def set_uppercase(self):
        self.uppercase = True

    def set_capitalize(self):
        self.capitalize = True

    def set_strip_extension(self):
        self.strip_extension = True

    def set_alpha(self):
        self.only_alpha = True

    def _feed_queue(self):
        for resource in self.payload:
            if self.only_alpha:
                if not resource.isalnum():
                    continue

            if self.uppercase:
                resource = resource.upper()

            if self.capitalize:
                resource = resource.capitalize()

            if self.strip_extension:
                resource = resource.split(".")[0]

            # Useful when looking for files without extension instead of directories
            if self.remove_slash and resource.endswith("/"):
                resource = resource[:-1]

            for extension in self.extensions:
                # If resource is a whole word and user didnt provide a extension
                # put a final /
                if (
                    not extension
                    and not _has_extension(resource)
                    and not self.remove_slash
                ):
                    resource += "/"

                # Put a . before extension if the users didnt do it
                if extension and not "." in extension:
                    extension = "." + extension

                self.task_id += 1
                task = Task(self.task_id, self.target, resource, extension)
                task.set_payload_filename(self.payload_filename)
                task.set_payload_length(self.get_total_requests())
                task.set_banned_response_codes(self.banned_response_codes)
                task.set_unbanned_response_codes(self.unbanned_response_codes)
                task.set_content(self.content)
                self.queue.put(task)
                self.number_of_tasks += 1

    def get_queue(self):
        if self.recursive:
            url_components = _get_url_components(self.target)
            # save main component (scheme + netloc)
            path = urlparse.urlparse(self.target).path
            saved_main_component = self.target[: self.target.find(path)]
            self.total_requests = (
                self.number_of_tasks * len(self.extensions) * len(url_components)
            )

            # if user select recursive but url is just root
            if len(url_components) == 1:
                self._feed_queue()
            else:
                # iterate over generated multiple paths
                for i in url_components:
                    self.target = saved_main_component + i
                    self._feed_queue()
        else:
            self.total_requests = self.number_of_tasks * len(self.extensions)
            self._feed_queue()
        return self.queue
