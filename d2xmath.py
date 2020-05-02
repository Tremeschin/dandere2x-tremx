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


from color import color_by_name

color = color_by_name("li_blue")

class D2XMath():
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
        """

        debug_prefix = "[D2XMath.set_block_size]"

        

        # As percentages annoying to set manually
        # This one looks like a good number
        if self.context.block_size == "auto":
            self.context.block_size = "1.85%"


        # self.context.* too long, YOLO
        block_size = self.context.block_size
        resolution = self.context.resolution
        width = resolution[0]
        height = resolution[1]


        # If the block_size is percentage-based, we basically round,
        # divide, multiply a few stuff to get a theoric block size
        # and "fit" it to the nearest 4 multiple as common resolutions
        # are really 4-multiple based

        if "%" in str(self.context.block_size):
            percentage = round(float(block_size.replace("%", "")) / 100, 6)
            video_dimensions_min = min(height, width)
            theoric_block_size = round(video_dimensions_min * percentage, 3)
            rounded_theoric = round(theoric_block_size)

            # Round $n$ to the nearest $base$ multiple ==> round = base * round(x/base)
            base = 4
            block_size = base * round(rounded_theoric / base)

            self.utils.log(color, debug_prefix, "Block size set to percentage:", percentage)
            self.utils.log(color, debug_prefix, "Video height:", height, " - Video width:", width)
            self.utils.log(color, debug_prefix, "Minimum value of video dimensions is:", video_dimensions_min)
            self.utils.log(color, debug_prefix, "Theoric block_size:", theoric_block_size)
            self.utils.log(color, debug_prefix, "Rounded theoric block_size:", rounded_theoric)
            self.utils.log(color, debug_prefix, "Fitted to nearest 4 multiple:", block_size)

            if block_size < 16:
                self.utils.log(color, debug_prefix, "Block_size is lower than 16, not ideal, hard limitting to 16.")
                block_size = 16
        

        self.utils.log(color, debug_prefix, "Setting final block_size to %s" % block_size)
        self.context.block_size = block_size



    # Function that sets the video resolution to the nearest multiple of the block_size
    def get_a_valid_input_resolution(self):

        debug_prefix = "[D2XMath.get_a_valid_input_resolution]"

        resolution = self.context.resolution
        width = resolution[0]
        height = resolution[1]
        
        block_size = self.context.block_size

        trueblock_size_multiples = [block_size*i for i in range(int(max(width, height)/block_size)*2)]

        # https://www.geeksforgeeks.org/python-find-closest-number-to-k-in-given-list/
        def closest_number_to(n, lst):
            return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-n))] 

        closest_width  = closest_number_to(width,  trueblock_size_multiples)
        closest_height = closest_number_to(height, trueblock_size_multiples)


        self.utils.log(color, debug_prefix, "Valid output resolution:")

        self.utils.log(color, self.context.indentation, "Original resolution: (%sx%s) (WxH)" % (width, height))
        self.utils.log(color, self.context.indentation, "Recieved block_size: %s" % block_size)     
        self.utils.log(color, self.context.indentation, "New valid resolution: (%sx%s) (WxH)" % (closest_width, closest_height))

        self.context.valid_resolution = [closest_width, closest_height]
