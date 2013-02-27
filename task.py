import os
import sys

class Task:

    def __init__(self, payload, target, resource, extension="", response_code=0,\
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

    def get_complete_target(self):
        return self.target + self.resource + self.extension

    def print_report(self):
        sys.stdout.write("{0} {1:^12} {2}".format( self.response_code, \
                                    self.response_size, \
                                    self.target + self.resource + self.extension \
                                    + os.linesep))