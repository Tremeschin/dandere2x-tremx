"""
===============================================================================

Purpose: Math functions for Dandere2x on deterministic factors

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


color = colors["white"]


class Dandere2xMath():
    def __init__(self, context, utils):
        self.context = context
        self.utils = utils

    def set_block_size(self):
        # Looks like the sweet spot for percentage block_size is 1.85%
        # Block_size in percentage is about the following:
        """
        Suppose we have an 1080p source video file, 20 pixels compared to
        the height 1080 pixels is about 1.85185185..% of the total.

        Now comparing those same 20 pixels to the same 1080p source file but
        downscaled to something like 480p, that's 4.1666..% of the 480 pixels

        This means that with this fixed 20 pixels, we actually "get" a lot
        more "area" in the 480p video compared to the 1080p. This is a way
        of "balancing" by getting a dynamic block_size which is set as a %.

        Though with new variable block size on right and bottom corner,
        it's not ideal for any (width or height) % block_size be a low value
        """

        debug_prefix = "[Dandere2xMath.set_block_size]"

        block_size = self.context.block_size
        resolution = self.context.resolution
        width = resolution[0]
        height = resolution[1]

        # As percentages annoying to set manually
        # This one looks like a good number
        if self.context.block_size == "auto":

            # If the block_size is percentage-based, we basically round,
            # divide, multiply a few stuff to get a theoric block size
            # and "fit" it to the nearest 4 multiple as common resolutions
            # are really 4-multiple based

            percentage = round(1.85 / 100, 6)
            block_size = round( min(height, width) * percentage )

            self.utils.log(color, 4, debug_prefix, "Block size set to percentage:", percentage)
            self.utils.log(color, 4, debug_prefix, "Video height:", height, " - Video width:", width)

            if block_size < 16:
                self.utils.log(color, 4, debug_prefix, "Block_size is lower than 16, not ideal, hard limitting to 16.")
                block_size = 16

            self.utils.log(color, 1, debug_prefix, "Block size auto is [%s]" % block_size)
            self.context.block_size = block_size

        else:
            # Do not change block_size
            self.utils.log(color, 4, debug_prefix, "Do not change block_size")
            pass

        # Checks stupid right / bottom edges blocks

        # Best case scenario, perfect fit
        if (width % block_size == 0) and (height % block_size == 0):
            return

        self.utils.log(color, 1, debug_prefix, "[ERROR] BLOCK_SIZE AUTO: THERE IS NO ALGORITHM TO FIX NOT PERFECT BLOCK_SIZE MATCH ACCORDING TO THE RESOLUTION: HERE'S THE REMAINDERS [Width: %s] [Height: %s], UPSCALE SHALL CONTINUE, BUT IF THOSE ARE LOW VALUES (EXCEPT ZERO) CONSIDER CHANGING BLOCK_SIZE" % (width % block_size, height % block_size)) 



if __name__ == "__main__":
    import misc.greeter_message
    print("You shouldn't be running this file directly, Dandere2x is class based and those are handled by dandere2x.py which is controlled by dandere2x_cli.py or a gui")
