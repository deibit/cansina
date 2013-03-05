class Task:
    ''' This class stores information retrieved from/to the request'''
    def __init__(self, number, payload, target, resource, extension=None,
        response_code=0, response_size=0, response_time=0, banned=None):
        self.number = number
        self.payload = payload
        self.target = target
        self.resource = resource
        self.extension = extension
        self.response_code = response_code
        self.response_size = response_size
        self.response_time = response_time
        self.valid = True
        self.banned = banned

    def set_response_code(self, code):
        self.response_code = str(code)
        if self.response_code in self.banned:
            self.valid = False

    def values(self):
        return (self.number,
                self.payload,
                self.target,
                self.resource,
                self.extension,
                self.response_code,
                self.response_size,
                self.response_time)

    def get_complete_target(self):
        return self.target + self.resource + self.extension

    def is_valid(self):
        return self.valid
