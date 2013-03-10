import multiprocessing

from task import Task

SLEEP_TIME = 0.1

class Payload(multiprocessing.Process):
    def __init__(self, target, payload, extension, banned_response_codes, content):
        multiprocessing.Process.__init__(self)
        self.target = target
        self.payload = payload
        self.extension = extension
        self.banned_response_codes = banned_response_codes
        self.queue = multiprocessing.JoinableQueue()
        self.payload_size = len(self.payload)
        self.payload_filename = payload.pop()
        self.banned_response_codes = banned_response_codes
        self.content = content

    def run(self):
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
                    self.queue.put(Task(number, self.payload_filename, self. payload_size, self.target, resource,
                                        extension, self.banned_response_codes, self.content))
                while self.queue.full():
                    time.sleep(SLEEP_TIME)

    def _comment(self, resource):
        '''Returns True is the resource starts with a comment sign'''
        for b in ['#']:
            if resource.startswith(b):
                return True
        return False