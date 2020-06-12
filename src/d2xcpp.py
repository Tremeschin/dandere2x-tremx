"""
===============================================================================

Purpose: Dandere2x C++ wrapper for python, calls the binary

Syntax:

binary input block_size width height out vectors start_frame bleed \
residuals_output use_mindisk zero_padding only_write_debug_video debug_video
show_debug_video_realtime show_block_matching_stats

NOTE: residuals_output must end in a os.path.sep -> "/path/to/dir/" and not
"/path/to/dir"

There are many option in the main.cpp after including things on the defines
like saving debug frames to video

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

from utils import SubprocessUtils
from color import colors
import time


color = colors["d2xcpp"]


class Dandere2xCPPWraper():

    def __init__(self, context, utils, controller, video, stats):

        debug_prefix = "[Dandere2xCPPWraper.__init__]"

        self.context = context
        self.utils = utils
        self.controller = controller
        self.video = video
        self.stats = stats

        # Get the binary of dandere2x_cpp according to the OS
        self.binary = self.utils.get_binary("dandere2x_cpp")

        self.utils.log(color, 2, debug_prefix, "Got binary: [%s]" % self.binary)

    # Generate a run command based on Context info
    def generate_run_command(self):

        debug_prefix = "[Dandere2xCPPWraper.generate_run_command]"

        # [TODO] Woof, hope I can get C++ accept something like: "dandere2x_cpp -i file -r residual_path"
        self.command = [
            self.binary,
            self.context.input_file,
            str(self.context.block_size),
            str(self.context.resolution[0]),
            str(self.context.resolution[1]),
            str(self.context.last_processing_frame),
            str(self.context.bleed),
            self.context.residual,
            str(int(self.context.mindisk)),
            str(self.context.zero_padding),
            str(int(self.context.write_debug_video)),
            self.context.debug_video,
            str(self.context.dark_threshold),
            str(self.context.bright_threshold),
            str(self.context.show_debug_video_realtime),
            str(self.context.show_block_matching_stats),
            str(self.context.only_run_dandere2x_cpp),
            str(self.context.upscale_full_frame_threshold)
        ]

        self.utils.log(color, 5, debug_prefix, "Run command is: %s" % self.command)
        self.utils.log(color, 5, debug_prefix, "[DEBUG] Plain command is: %s" % ' '.join(map(str, self.command)))

    # Run with SubprocessUtils the d2xcpp binary
    def run(self):

        debug_prefix = "[Dandere2xCPPWraper.run]"

        # Single run the subprocess
        self.subprocess = SubprocessUtils("d2xcpp", self.utils, self.context)
        self.subprocess.from_list(self.command)
        self.subprocess.run()

        # Until it has finished
        while self.subprocess.is_alive():
    
            # Get every line it has outputted
            for line in self.subprocess.realtime_output():

                # Lines with "|" are data Python needs
                if line.startswith("|"):
                    self.parse_cpp_out_newline(line)
                else:
                    self.utils.log(color, 1, debug_prefix, "[CPP] %s" % line)
                    
                # If we have finished, exit
                if line.startswith("|end"):
                    break            

            # Controller says to stop? goodbye
            if self.controller.stop == True:
                self.subprocess.terminate()
            
            # Wait a bit for not hanging this Python GIL
            time.sleep(0.1)

    # Parse newline of cpp_out, generic
    def parse_cpp_out_newline(self, line):

        debug_prefix = "[Dandere2xCPPWraper.parse_cpp_out_newline]"

        # A line syntax is the following:
        # |type;frame;data0,data1,data2...

        # Cut the first "|" as that means it's a data line, split
        line = line[1:]

        # Split it on the ";"
        line = line.split(";")

        # The type is always the first argument
        line_type = line[0]

        # Blocks lines are the ones with vector data from C++ block matching
        if line_type == "blocks":

            line_referred_frame = line[1]
            
            line_data = line[2][1:].split(",")

            self.controller.block_match_data[line_referred_frame] = {
                "type": line_type,
                "data": line_data
            }
        
        # Status to show on screen on how much the video has been recycled
        elif line_type == "recycled":
            self.stats.recycled_percentage = str(line[1])
        
        # Empty copies last merged frame as nothing has changed
        elif line_type == "empty":

            line_referred_frame = line[1]

            self.controller.block_match_data[line_referred_frame] = {
                "type": line_type,
                "data": None
            }

        # fullframe lines just loads the upscaled residual and pipes it
        elif line_type == "fullframe":

            line_referred_frame = line[1]

            self.controller.block_match_data[line_referred_frame] = {
                "type": line_type,
                "data": None
            }
        
        # End lines don't have data
        elif line_type == "end":

            line_referred_frame = line[1]

            self.controller.block_match_data[line_referred_frame] = {
                "type": line_type,
                "data": None
            }

        # Vectors are information on the blocks C++ will match and Python will replace
        elif line_type == "vector":

            # The vector id is the second part of the line and the data the remaining
            vector_id = line[1]
            vector_data = line[2]

            # The vector tuple are a set of 4 coordinates that says the position of the block
            vector_tuple = vector_data.split(",")

            # Convert them to ints as the lines we get are decoded texts
            vector_tuple = [int(n) for n in vector_tuple]

            # Assign them onto controller vectors
            self.controller.vectors[vector_id] = vector_tuple


if __name__ == "__main__":
    from utils import Miscellaneous
    print("You shouldn't be running this file directly, Dandere2x is class based and those are handled by dandere2x.py which is controlled by dandere2x_cli.py or a gui")
