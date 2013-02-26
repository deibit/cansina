class Task:

    def __init__(self, payload, target, resource, extension, response_code=0,\
        response_size=0, response_time=0):
        self.payload = payload
        self.target = target
        self.resource = resource
        self.extension = extension
        self.response_code = response_code
        self.response_size = response_size
        self.response_time = response_time

    def to_database(self):
        return (self.payload,
                self.target,
                self.resource,
                self.extension,
                self.response_code,
                self.response_size,
                self.response_time)

    def to_console(self):
        return "{0[0]:^6} {0[1]:^10} {0[0]}{1}".format( self.response_code, \
                                                        self.response_size,
                                                        self.resource + \
                                                        self.extension)

    def get_complete_target(self):
        return self.target + self.resource + self.extension

    def print_report(self):
        print "{0:3} {1:10} {2:30}".format( self.response_code, \
                                            self.response_size, \
                                            self.resource + self.extension)