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

                # Skip commented lines
                if resource and resource[0] == '#':
                    continue

                # Avoid double // because some dicts have /prepend_words
                if resource[0] == '/':
                    resource = resource[1:]

                for extension in self.extension:

                    # If resource is a whole word and user didnt provide a extension
                    # put a final /
                    if not extension and not '.' in resource:
                        resource = resource + '/'

                    # Put a . before extension if the users didnt do it
                    if extension and not '.' in extension:
                        extension = '.' + extension

                    self.queue.put(Task(number, self.payload_filename, self.payload_size, self.target, resource,
                                        extension, self.banned_response_codes, self.content))
                while self.queue.full():
                    time.sleep(SLEEP_TIME)

    def _comment(self, resource):
        '''Returns True is the resource starts with a comment sign'''
        for b in ['#']:
            if resource.startswith(b):
                return True
        return False