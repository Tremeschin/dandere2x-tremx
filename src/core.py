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

from color import colors
import threading
import time


color = colors["core"]


class Core():
    
    def __init__(self, context, utils, controller, upscaler, d2xcpp, processing, stats, video):
        self.context = context
        self.utils = utils
        self.controller = controller
        self.upscaler = upscaler
        self.d2xcpp = d2xcpp
        self.processing = processing
        self.stats = stats
        self.video = video

        self.ROOT = self.context.ROOT

    # Calls threads and
    def start(self):

        debug_prefix = "[Core.start]"

        # # Create the threads but don't start them yet
        # # Daemon mode to make them exit when we exit rather than being stuck

        # Create the Dandere2x C++ thread
        self.controller.threads["danderere2x_cpp_thread"] = threading.Thread(target=self.d2xcpp.run, daemon=True)
        self.utils.log(color, 3, debug_prefix, "Created thread Core.danderere2x_cpp_thread")

        # Create Processing.run thread
        self.controller.threads["processing"] = threading.Thread(target=self.processing.run, daemon=True)
        self.utils.log(color, 3, debug_prefix, "Created thread Core.processing")

        # For debugging purposes
        if self.context.enable_upscaler:

            # Create the upscaler thread pointing the input into the residuals and out to the upscaled
            self.controller.threads["upscaler_keep_upscaling"] = threading.Thread(
                target=self.upscaler.keep_upscaling,
                args=(self.context.residual, self.context.upscaled),
                daemon=True
            )

            self.utils.log(color, 3, debug_prefix, "Created thread upscaler.keep_upscaling")
        else:
            self.utils.log(colors["debug"], 0, debug_prefix, "[DEBUG] upscaler DISABLED IN DEBUG SETTINGS")

        # If set to show stats, create stats thread
        if self.context.show_stats:
            self.controller.threads["stats"] = threading.Thread(
                target=self.stats.start,
                daemon=True
            )

        # Create the ruthless residual eliminator thread, see its code for more info
        self.controller.threads["ruthless_residual_eliminator"] = threading.Thread(target=self.upscaler.ruthless_residual_eliminator)
        self.utils.log(color, 3, debug_prefix, "Created thread upscaler.ruthless_residual_eliminator")

        # Create the pipe write thread
        self.controller.threads["pipe_writer_loop"] = threading.Thread(target=self.video.ffmpeg.pipe_writer_loop)
        self.utils.log(color, 3, debug_prefix, "Created thread video.ffmpeg.pipe_writer_loop")
        
        # # Start the threads, warn the user that the output is no more linear

        self.utils.log(colors["debug"], 1, debug_prefix, "[WARNING] FROM NOW ON NO OUTPUT IS LINEAR AS THREADING STARTS")

        # For each thread, start them
        for thread in self.controller.threads:
            self.utils.log(color, 2, debug_prefix, "Starting thread: [\"%s\"]" % thread)
            self.controller.threads[thread].start()


if __name__ == "__main__":
    from utils import Miscellaneous
    Miscellaneous()
    print("You shouldn't be running this file directly, Dandere2x is class based and those are handled by dandere2x.py which is controlled by dandere2x_cli.py or the upcoming GUI")
