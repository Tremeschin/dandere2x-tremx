"""
===============================================================================

Purpose: Set of utilities for Dandere2x, miscellaneous functions, algo logging

===============================================================================

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.

===============================================================================
"""

# merge.py
# residual.py

# This file applies pframe, fade, corrections and calls merge
# Basically the "core" of Dandere2x

from color import rgb, debug_color

import threading

color = rgb(0, 115, 255)


class CoreLoop():
    def __init__(self, context, utils, controller, plugins, waifu2x):

        debug_prefix = "[CoreLoop.__init__]"

        self.context = context
        self.utils = utils
        self.controller = controller
        self.plugins = plugins
        self.waifu2x = waifu2x

        self.ROOT = self.context.ROOT


    def start(self):

        debug_prefix = "[CoreLoop.start]"

        self.utils.log(color, debug_prefix, "Threading CoreLoop.pipe_plugins")
        self.context.threads["pipe_plugin_thread"] = threading.Thread(target=self.pipe_plugins)
        
        self.context.threads["waifu2x_keep_upscaling"] = threading.Thread(
            target=self.waifu2x.keep_upscaling,
            args=(self.context.residual, self.context.upscaled)
        )

        self.utils.log(debug_color(), debug_prefix, "[WARNING] FROM NOW ON NO OUTPUT IS LINEAR AS THREADING STARTS")

        for thread in self.context.threads:
            self.utils.log(color, debug_prefix, "Starting thread: [\"%s\"]" % thread)
            self.context.threads[thread].start()
        
        




    # Reads and parses self.context.d2x_cpp_out file, send to plugins.py
    def pipe_plugins(self):

        debug_prefix = "[CoreLoop.pipe_plugins]"

        if self.context.loglevel >= 3:
            self.utils.log(debug_color(), debug_prefix, "[DEBUG] Printing new contents of file [%s]" % self.context.d2x_cpp_out)
            self.utils.log(debug_color(), debug_prefix, "[DEBUG] Will exit on first input")

        for newstuff in self.utils.updating_file(self.context.d2x_cpp_out):
            if self.context.loglevel >= 3:
                self.utils.log(debug_color(), debug_prefix, "[DEBUG]", newstuff)
                exit()



    def plugin_wrappers(self):
        pass

