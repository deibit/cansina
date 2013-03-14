class Task:

    content = None

    ''' This class stores information retrieved from/to the request'''
    def __init__(self, number, payload_filename, payload_size, target, resource, extension):

        self.number = number
        self.payload_filename = payload_filename
        self.payload_size = payload_size
        self.target = target
        self.resource = resource
        self.extension = extension

        self.location = ""
        self.response_code = None
        self.response_size = None
        self.response_time = None
        self.banned_response_codes = []

        self.valid = True
        self.content_detected = False

    def set_banned_response_codes(self, banned_codes):
        self.banned_response_codes = banned_codes

    def set_response_code(self, code):
        self.response_code = str(code)
        if self.response_code in self.banned_response_codes:
            self.valid = False

    def set_content(self, content):
        Task.content = content

    def get_content(self):
        return Task.content

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
