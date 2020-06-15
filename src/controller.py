"""
===============================================================================

Purpose: Non constant and runtime dependent variables for communicating
between Python scripts

Holds for example the block_match_data we parse with core.py and a signal to stop d2x

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
import sys


color = colors["controller"]


# This class is more used on the block_match_data, vectors and threads
# and communicating non static things between scripts
class Controller():
    def __init__(self, utils, context):

        self.utils = utils
        self.context = context

        self.stop = False
        self.upscale_finished = False
        self.percentage_completed = 0
        self.stats_list = []
        self.block_match_data = {}
        self.vectors = {}
        self.threads = {}

    def exit(self):

        debug_prefix = "[Controller.exit]"

        self.utils.log(color, 1, debug_prefix, "Controller exit called")

        if not self.upscale_finished:
            if not self.context.resume:
                self.utils.log(color, 0, debug_prefix, "Setting resume=True as we're closing")
                self.context.resume = True
        else:
            self.utils.log(color, 0, debug_prefix, "Exiting as upscale finished, Goodbye Dandere!!")

        self.stop = True



if __name__ == "__main__":
    from utils import Miscellaneous
    Miscellaneous()
    print("You shouldn't be running this file directly, Dandere2x is class based and those are handled by dandere2x.py which is controlled by dandere2x_cli.py or a gui")
