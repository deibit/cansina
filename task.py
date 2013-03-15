class Task:

    payload_length = 0
    payload_filename = None
    target = None
    banned_response_codes = []

    @staticmethod
    def set_payload_length(length):
        Task.payload_length = length

    @staticmethod
    def get_payload_length():
        return Task.payload_length

    @staticmethod
    def set_banned_response_codes(banned_codes):
        Task.banned_response_codes = banned_codes

    @staticmethod
    def set_payload_filename(payload_filename):
        Task.payload_filename = payload_filename

    @staticmethod
    def set_target(target):
        Task.target = target

    ''' This class stores information retrieved from/to the request'''
    def __init__(self, number, target, payload_filename, resource, extension):

        self.number = number
        self.resource = resource
        self.extension = extension
        self.content = None

        self.location = ""
        self.response_code = None
        self.response_size = None
        self.response_time = None
        self.valid = True
        self.content_detected = False

    def set_response_code(self, code):
        self.response_code = str(code)
        if self.response_code in Task.banned_response_codes:
            self.valid = False

    def set_location(self, location):
        self.location = location

    def set_content(self, content):
        self.content = content

    def get_content(self):
        return self.content

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
        if '***' in Task.target:
            Task.target = Task.target.replace('***', self.resource)
            return Task.target + self.extension
        return Task.target + self.resource + self.extension

    def is_valid(self):
        return self.valid

    def content_has_detected(self, value):
        self.content_detected = value
