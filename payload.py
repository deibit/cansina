from multiprocessing import JoinableQueue
from task import Task

class Payload():
    def __init__(self, target, payload, extension, banned_response_codes):
        self.payload_filename = payload.pop()
        self.payload = payload
        self.extension = extension
        self.banned_response_codes = banned_response_codes
        self.queue = JoinableQueue()
        self.size = len(self.payload)

        number = 0
        for resource in self.payload:
            number = number + 1
            # Asigning a line number to every payload-line
            # Cleaning spurious / of some payloads
            # Add . in extensions if it lacks
            if resource and resource[0] == '#':
                continue
            if resource and resource[0] == '/':
                resource = resource[1:]
            for extension in self.extension:
                if extension and not extension[0] == '.':
                    extension = '.' + extension
                self.queue.put(Task(number, self.payload_filename, target, resource,
                                    extension, self.banned_response_codes))

    def _comment(self, resource):
        '''Returns True is the resource starts with a comment sign'''
        for b in ['#']:
            if resource.startswith(b):
                return True
        return False