class Task:

    """ This class stores information retrieved from/to the request"""

    def __init__(self, number, target, resource, extension):

        self.number = number
        self.target = target
        self.resource = resource
        self.extension = extension
        self.thread = -1

        self.payload_length = 0
        self.payload_filename = None
        self.banned_response_codes = []
        self.unbanned_response_codes = []

        self.content = None
        self.location = ""
        self.response_code = None
        self.response_size = None
        self.response_time = None
        self.response_type = ""
        self.content_detected = False
        self.ignorable = True

    def set_payload_length(self, length):
        self.payload_length = length

    def get_payload_length(self):
        return self.payload_length

    def set_banned_response_codes(self, banned_codes):
        self.banned_response_codes = banned_codes

    def set_unbanned_response_codes(self, unbanned_codes):
        self.unbanned_response_codes = unbanned_codes

    def set_payload_filename(self, payload_filename):
        self.payload_filename = payload_filename

    def set_response_code(self, code):
        self.response_code = code
        # By default a code is valid but...if...
        # ...we select and optimistic detection 'all is valid' unless...
        if self.response_code in self.banned_response_codes:
            self.ignorable = True
        # ...but if we select a pesimistic one 'all is invalid' unless...
        elif self.response_code in self.unbanned_response_codes:
            self.ignorable = False

    def set_location(self, location):
        self.location = location

    def set_content(self, content):
        self.content = content

    def get_content(self):
        return self.content

    def get_number(self):
        return self.number

    def values(self):
        return (
            self.number,
            self.payload_filename,
            self.target,
            self.resource,
            self.extension,
            self.response_code,
            self.response_size,
            self.response_time,
            self.location,
        )

    def get_complete_target(self):
        if "***" in self.target:
            self.target = self.target.replace("***", self.resource.replace("/", ""))
            self.resource = ""
            return self.target + self.extension
        else:
            return self.target + self.resource + self.extension

    def content_has_detected(self, value):
        self.content_detected = value
