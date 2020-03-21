# merge.py
# residual.py

# This file applies pframe, fade, corrections and calls merge
# Basically the "core" of Dandere2x


class CoreLoop():
    def __init__(self, context, utils):

        debug_prefix = "[CoreLoop.__init__]"

        self.context = context
        self.utils = utils

        self.ROOT = self.context.ROOT



    def start(self):
        pass

