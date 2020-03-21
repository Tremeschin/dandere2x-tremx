# merge.py
# residual.py

# This file applies pframe, fade, corrections and calls merge
# Basically the "core" of Dandere2x

import threading

class CoreLoop():
    def __init__(self, context, utils, plugins):

        debug_prefix = "[CoreLoop.__init__]"

        self.context = context
        self.utils = utils
        self.plugins = plugins

        self.ROOT = self.context.ROOT

    def pipe_plugins(self):
        for line in self.utils.updating_file(self.context.d2x_cpp_out):
            print(line)

    def start(self):
        pipe_plugin_thread = threading.Thread(target=self.pipe_plugins)

        pipe_plugin_thread.start()


    def plugin_wrappers():
        pass

