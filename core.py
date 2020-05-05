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
import time


color = rgb(0, 115, 255)


class Core():
    def __init__(self, context, utils, controller, waifu2x, d2xcpp, processing):

        debug_prefix = "[Core.__init__]"

        self.context = context
        self.utils = utils
        self.controller = controller
        self.waifu2x = waifu2x
        self.d2xcpp = d2xcpp
        self.processing = processing

        self.ROOT = self.context.ROOT

        self.utils.log(color, debug_prefix, "Init")

    # Calls threads and
    def start(self):

        debug_prefix = "[Core.start]"

        self.controller.threads["pipe_plugin_thread"] = threading.Thread(target=self.get_new_d2xcpp_content_loop)
        self.utils.log(color, debug_prefix, "Created thread Core.pipe_plugin_thread")

        self.controller.threads["danderere2x_cpp_thread"] = threading.Thread(target=self.d2xcpp.run)
        self.utils.log(color, debug_prefix, "Created thread Core.danderere2x_cpp_thread")

        self.controller.threads["processing"] = threading.Thread(target=self.processing.run)
        self.utils.log(color, debug_prefix, "Created thread Core.processing")

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

    # # # These are "parsers" for the Dandere2x C++ part that loads the stuff we need (or not) into self.block_match_data

    # Parse newline of cpp_out, generic
    def parse_cpp_out_newline(self, line):

        debug_prefix = "[Core.parse_cpp_out_newline]"

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

        self.controller.block_match_data[line_referred_frame] = {
            "type": line_type,
            "data": data
        }

        return line

    # Decides if that line is necessary based on
    def is_necessary_line(self, line):

        debug_prefix = "[Core.is_necessary_line]"

        if self.context.loglevel >= 13:
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

        debug_prefix = "[Core.parse_whole_cpp_out]"


        self.utils.log(color, debug_prefix, "Parsing whole cpp_out file")

        # Warn the user we'll be getting everything as it is not a resume session
        if not self.context.resume:
            self.utils.log(color, debug_prefix, "GETTING EVERYTHING AS IS NOT RESUME SESSION")

        with open(self.context.d2x_cpp_plugins_out, "r") as cppout:
            for line in cppout:
                if not line == "END":
                    if self.is_necessary_line(line):
                        self.parse_cpp_out_newline(line)

        if self.context.loglevel >= 10:
            self.utils.log(color, debug_prefix, "[DEBUG 5] Contents of controller.block_match_data:")
            self.utils.log(color, debug_prefix, self.controller.block_match_data)

    def get_d2xcpp_vectors(self):

        debug_prefix = "[Core.get_d2xcpp_vectors]"

        # Wait for d2x_cpp_vectors_out to write END on the last line of file file
        while True:

            lastline = ""

            with open(self.context.d2x_cpp_vectors_out, "r") as vectors:
                for line in vectors:
                    lastline = line

            if lastline == "END":
                break

            if self.controller.stop:
                return -1

            self.utils.log(color, debug_prefix, "Waiting for last line in d2x_cpp_vectors_out to be \"END\"")
            time.sleep(0.2)

        self.utils.log(color, debug_prefix, "Got vectorfile contents")

        self.utils.log(color, debug_prefix, "Parsing Dandere2x C++ vectors file")

        with open(self.context.d2x_cpp_vectors_out, "r") as vectorfile:
            for line in vectorfile:
                if not line == "END":
                    # 0;(0,0,20,20)
                    # 5162;(1900,640,1920,660) --> ["5162", "(1900,640,1920,660)"]

                    line = line.split(";")

                    vector_id = line[0]

                    # ["5162", "(1900,640,1920,660)"] --> "(1900,640,1920,660)" --> 1900,640,1920,660 --> ["1900", "640", "1920", "660"]
                    vector_tuple = line[1]

                    vector_tuple = vector_tuple.replace("(", "")
                    vector_tuple = vector_tuple.replace(")", "")
                    vector_tuple = vector_tuple.split(",")

                    vector_tuple = [int(n) for n in vector_tuple]

                    # Create entry in dictionary, line[0] = 5162
                    self.controller.vectors[vector_id] = vector_tuple

        if self.context.loglevel >= 12:
            self.utils.log(color, debug_prefix, "[DEBUG 5] Contents of controller.vectors:")
            self.utils.log(color, debug_prefix, self.controller.vectors)

    # Reads new content of self.context.d2x_cpp_out file
    def get_new_d2xcpp_content_loop(self):

        debug_prefix = "[Core.get_new_d2xcpp_content_loop]"

        # Debug
        if self.context.loglevel >= 12:
            self.utils.log(debug_color(), debug_prefix, "[DEBUG] Printing new contents of file [%s]" % self.context.d2x_cpp_plugins_out)

        # Get the new stuff APPENDED into the file
        for newstuff in self.utils.updating_file(self.context.d2x_cpp_plugins_out):

            # TODO GET A SAFE WAY OF WAITING D2XCPP TO WRITE TO PLUGINS OUT FILE, TEMPORARY SLEEP
            time.sleep(0.016)

            self.parse_cpp_out_newline(newstuff)

            # Debug
            if self.context.loglevel >= 12:
                self.utils.log(debug_color(), debug_prefix, "[DEBUG]", newstuff.replace("\n", ""))
                self.utils.log(debug_color(), debug_prefix, "[DEBUG]", self.controller.block_match_data)
