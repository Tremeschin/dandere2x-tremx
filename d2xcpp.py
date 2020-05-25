"""
===============================================================================

Purpose: Dandere2x C++ wrapper for python, calls the binary

Syntax:

binary input block_size width height out vectors start_frame bleed \
residuals_output use_mindisk zero_padding only_write_debug_video debug_video

Example:

dandere2x_cpp "in.mkv" 40 1920 1080 "out.d2x" "vectors.d2x" 3 1 "residuals/" \
1 8 1 "debug.mkv"

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
from color import rgb

import time


color = rgb(240, 100, 64)


class Dandere2xCPPWraper():
    def __init__(self, context, utils, controller, video):
        debug_prefix = "[Dandere2xCPPWraper.__init__]"

        self.context = context
        self.utils = utils
        self.controller = controller
        self.video = video

        # Get the binary of dandere2x_cpp according to the OS
        self.binary = self.utils.get_binary("dandere2x_cpp")

        self.utils.log(color, debug_prefix, "Got binary: [%s]" % self.binary)

    # Generate a run command based on Context info
    def generate_run_command(self):

        debug_prefix = "[Dandere2xCPPWraper.generate_run_command]"

        self.command = [
            self.binary,
            self.context.input_file,
            str(self.context.block_size),
            str(self.context.resolution[0]),
            str(self.context.resolution[1]),
            self.context.d2x_cpp_plugins_out,
            self.context.d2x_cpp_vectors_out,
            str(self.context.last_processing_frame),
            str(self.context.bleed),
            self.context.residual,
            str(int(self.context.mindisk)),
            str(self.context.zero_padding),
            str(int(self.context.write_only_debug_video)),
            self.context.debug_video
        ]

        self.utils.log(color, debug_prefix, "Run command is: %s" % self.command)
        self.utils.log(color, debug_prefix, "[DEBUG] Plain command is: %s" % ' '.join(self.command))

    # Run with SubprocessUtils the d2xcpp binary
    def run(self):

        self.subprocess = SubprocessUtils("d2xcpp", self.utils)

        self.subprocess.from_list(self.command)

        self.subprocess.run()

        while self.subprocess.is_alive():
            time.sleep(0.5)
            if self.controller.stop is True:
                self.subprocess.terminate()


if __name__ == "__main__":
    print("You shouldn't be running this file directly, Dandere2x is class based and those are handled by dandere2x.py which is controlled by dandere2x_cli.py or the upcoming GUI")
