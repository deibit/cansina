from multiprocessing import JoinableQueue
from task import Task

class Payload():
    def __init__(self, target, payload, extension, banned_response_codes, content):
        self.payload = payload
        self.extension = extension
        self.banned_response_codes = banned_response_codes
        self.queue = JoinableQueue()
        self.payload_size = len(self.payload)

        payload_filename = payload.pop()

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
                self.queue.put(Task(number, payload_filename, self. payload_size, target, resource,
                                    extension, banned_response_codes, content))

    def _comment(self, resource):
        '''Returns True is the resource starts with a comment sign'''
        for b in ['#']:
            if resource.startswith(b):
                return True
        return False