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
        self.valid = True

    def values(self):
        return (self.payload,
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
