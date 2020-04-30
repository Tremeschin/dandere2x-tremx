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


from color import rgb, debug_color

import threading

color = rgb(0, 115, 255)


class CoreLoop():
    def __init__(self, context, utils, controller, plugins, waifu2x, d2xcpp):

        debug_prefix = "[CoreLoop.__init__]"

        self.context = context
        self.utils = utils
        self.controller = controller
        self.plugins = plugins
        self.waifu2x = waifu2x
        self.d2xcpp = d2xcpp

        self.ROOT = self.context.ROOT

        self.utils.log(color, debug_prefix, "Init")


    # Calls threads and 
    def start(self):

        debug_prefix = "[CoreLoop.start]"


        self.controller.threads["pipe_plugin_thread"] = threading.Thread(target=self.pipe_plugins)
        self.utils.log(color, debug_prefix, "Created thread CoreLoop.pipe_plugin_thread")


        self.controller.threads["danderere2x_cpp_thread"] = threading.Thread(target=self.d2xcpp.run)
        self.utils.log(color, debug_prefix, "Created thread CoreLoop.danderere2x_cpp_thread")
        
        
        # For debugging purposes
        if self.context.enable_waifu2x:
            
            # Create the waifu2x thread pointing the input into the residuals and out to the upscaled
            self.controller.threads["waifu2x_keep_upscaling"] = threading.Thread(
                target=self.waifu2x.keep_upscaling,
                args=(self.context.residual, self.context.upscaled)
            )

            self.utils.log(color, debug_prefix, "Created thread Waifu2x.keep_upscaling")

        else:
            self.utils.log(debug_color(), debug_prefix, "[DEBUG] WAIFU2X DISABLED IN DEBUG SETTINGS")



        # Start the threads, warn the user that the output is no more linear
        self.utils.log(debug_color(), debug_prefix, "[WARNING] FROM NOW ON NO OUTPUT IS LINEAR AS THREADING STARTS")

        for thread in self.controller.threads:
            self.utils.log(color, debug_prefix, "Starting thread: [\"%s\"]" % thread)
            self.controller.threads[thread].start()
        

    # # # These are "parsers" for the Dandere2x C++ part that loads the stuff we need (or not) into self.cpp_data


    # Parse newline of cpp_out, generic
    def parse_cpp_out_newline(self, line):

        debug_prefix = "[CoreLoop.parse_cpp_out_newline]"

        #if self.context.loglevel >= 4:
        #    self.utils.log(color, debug_prefix, "[DEBUG 4] Parsing line [\"%s\"]" % line)

        # A line syntax is the following:
        # type;frame-data0;data1;data2...


        # ["type;frame", "data0;data1;data2..."]
        line = line.split("-")

        # ";data0;data1;data2..." --> "data0;data1;data2..."
        data = line[1][1:].replace("\n", "")

        # type;frame-data0;data1;data2...  --> "type;frame" --> ["type", "frame"]
        line = line[0].split(";")

        line_type = line[0]
        line_referred_frame = line[1]

        self.controller.cpp_data[line_referred_frame] = {
            "type": line_type,
            "data": data
        }

        return line
        

    # Decides if that line is necessary based on 
    def is_necessary_line(self, line):

        debug_prefix = "[CoreLoop.is_necessary_line]"

        if self.context.loglevel >= 7:
            self.utils.log(color, debug_prefix, "[DEBUG] Checking if line [\"%s\"] is necessary: " % line)

        line = self.parse_cpp_out_newline(line)

        # If it isn't resume we gotta have everything
        if not self.context.resume:
            return True

        else:
        
            # TODO: CHECK IF NECESSARY IF NOT RESUME

            return True



    # For resume sessions, parse the entire cpp_out file
    def parse_whole_cpp_out(self):

        debug_prefix = "[CoreLoop.parse_whole_cpp_out]"

        self.utils.log(color, debug_prefix, "Parsing whole cpp_out file")

        # Warn the user we'll be getting everything as it is not a resume session
        if not self.context.resume:
            self.utils.log(color, debug_prefix, "GETTING EVERYTHING AS IS NOT RESUME SESSION")

        with open(self.context.d2x_cpp_plugins_out, "r") as cppout:
            for line in cppout:
                if self.is_necessary_line(line):
                    self.parse_cpp_out_newline(line)


        if self.context.loglevel >= 5:
            self.utils.log(color, debug_prefix, "[DEBUG 5] Contents of controller.cpp_data:")
            self.utils.log(color, debug_prefix, self.controller.cpp_data)
    

    # # #


    # Reads new content of self.context.d2x_cpp_out file
    def pipe_plugins(self):

        debug_prefix = "[CoreLoop.pipe_plugins]"

        # Debug
        if self.context.loglevel >= 3:
            self.utils.log(debug_color(), debug_prefix, "[DEBUG] Printing new contents of file [%s]" % self.context.d2x_cpp_plugins_out)

        # Get the new stuff APPENDED into the file
        for newstuff in self.utils.updating_file(self.context.d2x_cpp_plugins_out):
            
            # Debug
            if self.context.loglevel >= 3:
                self.utils.log(debug_color(), debug_prefix, "[DEBUG]", newstuff.replace("\n", ""))
                
            self.parse_cpp_out_newline(newstuff)



