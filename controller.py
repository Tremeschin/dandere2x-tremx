"""
Non static variables for communicating in between files
""" 


class Controller():
    def __init__(self):
        self.stop = False

    def exit(self):
        self.stop = True

