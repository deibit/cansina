from multiprocessing import JoinableQueue
from task import Task

class Payload():
    def __init__(self, target, payload_filename, extensions = [""]):
        self.queue = JoinableQueue()
        #
        # Creating the payload. Also we clean the resource stripping the string
        # before including it in the list.
        #
        self.payload = ""
        with open(payload_filename) as payload:
            self.payload = [i.strip() for i in payload.readlines() if not self._banned(i)]
        self.size = len(self.payload)
        #
        # TODO support for multiple extensions via generators
        #
        for resource in self.payload:
            self.queue.put(Task(payload_filename, target, resource, extensions[0]))

    def _banned(self, resource):
        '''Returns True is the resource starts with a comment sign'''
        for b in ['#']:
            if resource.startswith(b):
                return True
        return False