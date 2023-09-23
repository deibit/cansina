class Resumer:
    def __init__(self, args, line):
        self.args = args
        self.line = line

    def set_line(self, l):
        self.line = l

    def get_line(self):
        return self.line

    def get_args(self):
        return self.args
