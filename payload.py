from multiprocessing import JoinableQueue
from task import Task

class Payload():
    def __init__(self, target, payload_filename, extensions=[""], banned=[]):
        self.queue = JoinableQueue()
        self.banned = banned
        #
        # Creating the payload. Also we clean the resource stripping the string
        # before including it in the list.
        #
        self.payload = ""
        with open(payload_filename) as payload:
            self.payload = [i.strip() for i in payload.readlines() if not self._comment(i)]
        self.size = len(self.payload)
        #
        # TODO support for multiple extensions via generators
        #
        id = 0
        for resource in self.payload:
            id = id + 1
            self.queue.put(Task(id, payload_filename, target, resource, extensions[0], banned=self.banned))

    def _comment(self, resource):
        '''Returns True is the resource starts with a comment sign'''
        for b in ['#']:
            if resource.startswith(b):
                return True
        return False