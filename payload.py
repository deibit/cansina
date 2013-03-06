from multiprocessing import JoinableQueue
from task import Task

class Payload():
    def __init__(self, target, payload, extensions, banned_response_codes):
        self.payload_filename = payload.pop()
        self.payload = payload
        self.extensions = extensions
        self.banned_response_codes = banned_response_codes
        self.queue = JoinableQueue()
        self.size = len(self.payload)

        number = 0
        for resource in self.payload:
            # Asigning a line number to every payload-line
            number = number + 1
            # Cleaning spurious / of some payloads
            if resource[0] == '/':
                resource = resource[1:]
            self.queue.put(Task(number, self.payload_filename, target, resource,
                                self.extensions, self.banned_response_codes))

    def _comment(self, resource):
        '''Returns True is the resource starts with a comment sign'''
        for b in ['#']:
            if resource.startswith(b):
                return True
        return False