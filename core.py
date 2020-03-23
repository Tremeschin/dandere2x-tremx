# merge.py
# residual.py

# This file applies pframe, fade, corrections and calls merge
# Basically the "core" of Dandere2x

from color import *

import threading

color = rgb(0, 115, 255)


class CoreLoop():
    def __init__(self, context, utils, plugins):

        debug_prefix = "[CoreLoop.__init__]"

        self.context = context
        self.utils = utils
        self.plugins = plugins

        self.ROOT = self.context.ROOT

        self.utils.log(color, debug_prefix, "INIT")


    def start(self):
        pipe_plugin_thread = threading.Thread(target=self.pipe_plugins)

        pipe_plugin_thread.start()


    # Reads and parses self.context.d2x_cpp_out file, send to plugins.py
    def pipe_plugins(self):

        debug_prefix = "[CoreLoop.pipe_plugins]"

        if self.context.debug:
            self.utils.log(debug_color(), debug_prefix, "[DEBUG] Printing new contents of file [%s]" % self.context.d2x_cpp_out)

        for newstuff in self.utils.updating_file(self.context.d2x_cpp_out):
            if self.context.debug:
                self.utils.log(debug_color(), debug_prefix, "[DEBUG]", newstuff)



    def plugin_wrappers():
        pass

