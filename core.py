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
    def __init__(self, context, utils, controller, waifu2x, d2xcpp, processing, stats):

        debug_prefix = "[Core.__init__]"

        self.context = context
        self.utils = utils
        self.controller = controller
        self.waifu2x = waifu2x
        self.d2xcpp = d2xcpp
        self.processing = processing
        self.stats = stats

        self.ROOT = self.context.ROOT

    # Calls threads and
    def start(self):

        debug_prefix = "[Core.start]"

        self.controller.threads["danderere2x_cpp_thread"] = threading.Thread(target=self.d2xcpp.run, daemon=True)
        self.utils.log(color, 3, debug_prefix, "Created thread Core.danderere2x_cpp_thread")

        self.controller.threads["processing"] = threading.Thread(target=self.processing.run, daemon=True)
        self.utils.log(color, 3, debug_prefix, "Created thread Core.processing")

        # For debugging purposes
        if self.context.enable_waifu2x:

            # Create the waifu2x thread pointing the input into the residuals and out to the upscaled
            self.controller.threads["waifu2x_keep_upscaling"] = threading.Thread(
                target=self.waifu2x.keep_upscaling,
                args=(self.context.residual, self.context.upscaled),
                daemon=True
            )

            self.utils.log(color, 3, debug_prefix, "Created thread Waifu2x.keep_upscaling")

        else:
            self.utils.log(colors["debug"], 0, debug_prefix, "[DEBUG] WAIFU2X DISABLED IN DEBUG SETTINGS")

        if self.context.show_stats:
            self.controller.threads["stats"] = threading.Thread(
                target=self.stats.start,
                daemon=True
            )

        self.controller.threads["ruthless_residual_eliminator"] = threading.Thread(target=self.waifu2x.ruthless_residual_eliminator)
        self.utils.log(color, 3, debug_prefix, "Created thread Waifu2x.ruthless_residual_eliminator")
        
        # Start the threads, warn the user that the output is no more linear
        self.utils.log(colors["debug"], 1, debug_prefix, "[WARNING] FROM NOW ON NO OUTPUT IS LINEAR AS THREADING STARTS")

        for thread in self.controller.threads:
            self.utils.log(color, 2, debug_prefix, "Starting thread: [\"%s\"]" % thread)
            self.controller.threads[thread].start()


if __name__ == "__main__":
    print("You shouldn't be running this file directly, Dandere2x is class based and those are handled by dandere2x.py which is controlled by dandere2x_cli.py or the upcoming GUI")
