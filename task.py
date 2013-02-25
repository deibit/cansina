class Task:

    def __init__(self, payload, url, resource, extension, response_code,\
        response_size, response_time):
        self.payload = payload
        self.url = url
        self.resource = resource
        self.extension = extension
        self.response_code = response_code
        self.response_size = response_size
        self.response_time = response_time

    def to_database(self):
        return (self.payload,
                self.url,
                self.resource,
                self.extension,
                self.response_code,
                self.response_size,
                self.response_time)