"""
===============================================================================

Purpose: Non constant and runtime dependent variables for communicating
between Python scripts

Holds for example the cpp_data we parse with core.py and a signal to stop d2x

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

from color import rgb

color = rgb(240, 100, 64)

class Controller():
    def __init__(self, utils, context):

        self.utils = utils
        self.context = context

        self.stop = False
        self.cpp_data = {}
        self.vectors = {}
        self.threads = {}

    def exit(self):

        debug_prefix = "[Controller.exit]"

        self.utils.log(color, debug_prefix, "Controller exit called")

        if not self.context.resume:
            self.utils.log(color, debug_prefix, "Setting resume=True as we're closing")
            self.context.resume = True

        self.stop = True
