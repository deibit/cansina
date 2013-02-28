from multiprocessing import JoinableQueue
from task import Task

class Payload():
    size = 0
    def __init__(self, target, payload_filename, extensions = [""]):
        self.queue = JoinableQueue()
        self.payload = ""
        with open(payload_filename) as payload:
            self.payload = payload.readlines()
        Payload.size = len(self.payload)
        #
        # TODO support for multiple extensions via generators
        #
        for resource in self.payload:
            if not target[-1] == '/':
                target = target + '/'
            resource = resource.strip()
            if resource[0] == '/':
                resource = resource[1:]
            self.queue.put(Task(payload_filename, target, resource, extensions[0]))
