class Task:
    ''' This class stores information retrieved from/to the request'''
    def __init__(self, number, payload_filename, payload_size, target, resource, extension,
                banned_response_codes, content):

        self.number = number
        self.payload_filename = payload_filename
        self.payload_size = payload_size
        self.target = target
        self.resource = resource
        self.extension = extension
        self.banned = banned_response_codes
        self.content = content

        self.location = ""
        self.response_code = None
        self.response_size = None
        self.response_time = None

        self.valid = True
        self.content_detected = False

    def set_response_code(self, code):
        self.response_code = str(code)
        if self.response_code in self.banned:
            self.valid = False

    def values(self):
        return (self.number,
                self.payload_filename,
                self.target,
                self.resource,
                self.extension,
                self.response_code,
                self.response_size,
                self.response_time,
                self.location)

    def get_complete_target(self):
        if '***' in self.target:
            self.target = self.target.replace('***', self.resource)
            return self.target + self.extension
        return self.target + self.resource + self.extension

    def is_valid(self):
        return self.valid

    def content_has_detected(self, value):
        self.content_detected = value
