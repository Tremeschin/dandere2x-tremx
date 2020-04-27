"""
===============================================================================

Purpose: Wrapper for Numpy arrays and PIL Image, we call images Frames

Can load, copy, duplicate, save and substitute vectors of pixels

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

from color import rgb, color_by_name
from scipy import misc
from PIL import Image

import numpy as np

import imageio
import numpy
import time
import os


color = rgb(196, 255, 33)



class Frame():
    """
    An image class for Dandere2x that wraps around the numpy library.

    usage:

    frame = Frame()
    frame.load_from_path(self.context.ROOT + os.path.sep + "yn.jpg")

    frame2 = Frame()
    frame2.new(1920, 1080)
    
    frame2.duplicate(frame)
    
    frame2.save("yn_copy.jpg")

    """

    def __init__(self, context, utils, controller):

        self.context = context
        self.utils = utils
        self.controller = controller

        self.frame = None
        self.width = None
        self.height = None
        self.name = None
        


    # fuck this function, lmao. Credits to
    # https://stackoverflow.com/questions/52702809/copy-array-into-part-of-another-array-in-numpy
    def copy_from(self, A, B, A_start, B_start, B_end):
        """
        A_start is the index with respect to A of the upper left corner of the overlap
        B_start is the index with respect to B of the upper left corner of the overlap
        B_end is the index of with respect to B of the lower right corner of the overlap
        """

        debug_prefix = "[Frame.copy_from]"

        try:
            A_start, B_start, B_end = map(np.asarray, [A_start, B_start, B_end])
            shape = B_end - B_start
            B_slices = tuple(map(slice, B_start, B_end + 1))
            A_slices = tuple(map(slice, A_start, A_start + shape + 1))
            B[B_slices] = A[A_slices]

            if self.context.loglevel >= 3:
                self.utils.log(color, debug_prefix, "Copied from, args = {%s, %s, %s}" % (A_start, B_start, B_end))

        except ValueError:
            self.utils.log(color_by_name("li_red"), debug_prefix, "Fatal error copying block")
            self.controller.exit()


    # we need to parse the new input into a non uint8 format so it doesnt overflow,
    # then parse it back to an integer using np.clip to make it fit within [0,255]
    # If we don't do this,  numpy will overflow it for us and give us bad results.
    def copy_from_fade(self, A, B, A_start, B_start, B_end, scalar):
        """
        A_start is the index with respect to A of the upper left corner of the overlap
        B_start is the index with respect to B of the upper left corner of the overlap
        B_end is the index of with respect to B of the lower right corner of the overlap
        """

        debug_prefix = "[Frame.copy_from]"

        try:
            A_start, B_start, B_end = map(np.asarray, [A_start, B_start, B_end])
            shape = B_end - B_start
            B_slices = tuple(map(slice, B_start, B_end + 1))
            A_slices = tuple(map(slice, A_start, A_start + shape + 1))

            int_copy = numpy.copy(A[A_slices]).astype(int)  # use 'int_copy' instead of raw array to prevent overflow
            B[B_slices] = numpy.clip(int_copy + scalar, 0, 255).astype(np.uint8)

            if self.context.loglevel >= 3:
                self.utils.log(color, debug_prefix, "Copied from fade, args = {%s, %s, %s, %s}" % (A_start,B_start,B_end,scalar))

        except ValueError:
            self.utils.log(color_by_name("li_red"), debug_prefix, "Fatal error copying block from fade")
            self.controller.exit()


    # Create and set new frame
    def new(self, width, height):

        debug_prefix = "[Frame.new]"

        self.frame = np.zeros([height, width, 3], dtype=np.uint8)
        self.width = width
        self.height = height
        self.resolution = (width, height)
        self.name = ''

        if self.context.loglevel >= 3:
            self.utils.log(color, debug_prefix, "Resolution: [%sx%s]" % (width, height))


    # Load file based on nme
    def load_from_path(self, filename):

        debug_prefix = "[Frame.load_from_path]"

        if self.context.loglevel >= 3:
            self.utils.log(color, debug_prefix, "Name: [%s]" % filename)

        self.frame = imageio.imread(filename).astype(np.uint8)
        self.height = self.frame.shape[0]
        self.width = self.frame.shape[1]
        self.resolution = (self.width, self.height)
        self.name = filename

        if self.context.loglevel >= 3:
            self.utils.log(color, debug_prefix, "Resolution: [%sx%s]" % (self.width, self.height))


    # Wait on a file if it does not exist yet. Wait can be cancelled via a cancellation token
    def load_from_path_wait(self, filename):

        debug_prefix = "[Frame.load_from_path_wait]"

        if self.context.loglevel >= 3:
            self.utils.log(color, debug_prefix, "Waiting for: [%s]" % filename)

        self.utils.until_exists()
        self.load_from_path(filename)


    # Save an image with specific instructions depending on it's extension type.
    def save(self, directory):

        debug_prefix = "[Frame.save]"

        extension = os.path.splitext(os.path.basename(directory))[1]

        if self.context.loglevel >= 3:
            self.utils.log(color, debug_prefix, "Saving to file: [%s], extension is: [%s]" % (directory, extension))

        if 'jpg' in extension:
            jpegsave = self.image_array()
            jpegsave.save(directory + "temp" + extension, format='JPEG', subsampling=0, quality=100)
            self.utils.until_exist(directory + "temp" + extension)
            self.utils.rename(directory + "temp" + extension, directory)
        
        elif "png" in extension:
            save_image = self.image_array()
            save_image.save(directory + "temp" + extension, format='PNG')
            self.utils.until_exist(directory + "temp" + extension)
            self.utils.rename(directory + "temp" + extension, directory)


    # Get PIL image array from this object frame
    def image_array(self):
        return Image.fromarray(self.frame.astype(np.uint8))


    # Explained inside
    def save_image_temp(self, directory, temp_location):
        """
        Save an image in the "temp_location" folder to prevent another program from accessing the file
        until it's done writing.

        This is done to prevent other parts from using an image until it's entirely done writing.
        """

        debug_prefix = "[Frame.save_image_temp]"

        if self.context.loglevel >= 3:
            self.utils.log(color, debug_prefix, "Saving to dir [%s] with temp dir [%s]" % (directory, temp_location))

        self.save_image(temp_location)
        self.utils.until_exist(temp_location)
        self.utils.rename(temp_location, directory)


    # Gets the (other_frame), (self.frame), and set to this (self.frame) the other's (self.frame)
    def duplicate(self, other_frame):
        """
        Copy another image into this image using the self.copy_from numpy command. It seems that numpy affects
        the RGB contents of an image, so when another image needs to be copied, rather than copying the file itself,
        load it into a Frame, copy the Frame, then save the Frame, as opposed to copying the file itself.

        This ensure the images stay consistent temporally.
        """

        debug_prefix = "[Frame.duplicate]"

        if self.context.loglevel >= 3:
            self.utils.log(color, debug_prefix, "Duplicating from other_frame")

        height_matches = self.height == other_frame.height
        width_matches = self.width == other_frame.width


        # Checks if both height and width matches and if not log the info on what went wrong, exit Dandere2x
        if not height_matches or not width_matches:
            self.utils.log(color_by_name("li_red"), debug_prefix, "Copy images are not equal")

            errormessage = "Width matches: [%s], Height matches: [%s]" % (width_matches, height_matches)
            errormessage += " | This res: [%sx%s], Other res: [%sx%s]" % (self.width, self.height, other_frame.width, other_frame.height)

            self.utils.log(color_by_name("li_red"), debug_prefix, errormessage)

            self.controller.exit()


        self.copy_from(other_frame.frame, self.frame, (0, 0), (0, 0),
                  (other_frame.frame.shape[0], other_frame.frame.shape[1]))


    # Copy block from (other frame) to (this frame)
    def copy_block(self, other_frame, block_size, other_x, other_y, this_x, this_y):
        """
        Check that we can validly copy a block before calling the numpy self.copy_from method. This way, detailed
        errors are given, rather than numpy just throwing an un-informative error.
        """

        debug_prefix = "[Frame.copy_block]"

        if self.context.loglevel >= 3:
            self.utils.log(color, debug_prefix, "Copy block, from [%s] to [%s], checking valid" % (self.name, other_frame.name))

        # Check if inputs are valid before calling numpy self.copy_from
        self.check_valid(other_frame, block_size, other_x, other_y, this_x, this_y)

        self.copy_from(other_frame.frame, self.frame,
                  (other_y, other_x), (this_y, this_x),
                  (this_y + block_size - 1, this_x + block_size - 1))


    def fade_block(self, this_x, this_y, block_size, scalar):
        """
        Apply a scalar value to the RGB values for a given block. The values are then clipped to ensure
        they don't overflow.
        """

        debug_prefix = "[Frame.fade_block]"

        if self.context.loglevel >= 3:
            self.utils.log(color, debug_prefix, "Copy from fade: [%s]" % self.name)

        self.copy_from_fade(self.frame, self.frame,
                       (this_y, this_x), (this_y, this_x),
                       (this_y + block_size - 1, this_x + block_size - 1), scalar)


    def check_valid(self, other_frame, block_size, other_x, other_y, this_x, this_y):
        """
        Provide detailed reasons why a copy_block will not work before it's called. This method should access
        every edge case that could prevent copy_block from successfully working.
        """

        debug_prefix = "[Frame.check_valid]"

        if self.context.loglevel >= 3:
            self.utils.log(color, debug_prefix, "Checking valid, this frame: [%s], other frame: [%s]" % (self.name, other_frame.name))

        if this_x + block_size - 1 > self.width or this_y + block_size - 1 > self.height:
            self.utils.log(color_by_name("li_red"), debug_prefix, 'Input Dimensions Invalid for Copy Block Function, printing variables. Send Tyler this!')

            # Print Out Degenerate Values
            self.utils.log(color_by_name("li_red"), debug_prefix, 'this_x + block_size - 1 > self.width')
            self.utils.log(color_by_name("li_red"), debug_prefix, str(this_x + block_size - 1) + '?>' + str(self.width))

            self.utils.log(color_by_name("li_red"), debug_prefix, 'this_y + block_size - 1 > self.height')
            self.utils.log(color_by_name("li_red"), debug_prefix, str(this_y + block_size - 1) + '?>' + str(self.height))

            self.controller.exit()

        if other_x + block_size - 1 > other_frame.width or other_y + block_size - 1 > other_frame.height:
            self.utils.log(color_by_name("li_red"), debug_prefix, 'Input Dimensions Invalid for Copy Block Function, printing variables. Send Tyler this!')

            # Print Out Degenerate Values
            self.utils.log(color_by_name("li_red"), debug_prefix, 'other_x + block_size - 1 > other_frame.width')
            self.utils.log(color_by_name("li_red"), debug_prefix, str(other_x + block_size - 1) + '?>' + str(other_frame.width))

            self.utils.log(color_by_name("li_red"), debug_prefix, 'other_y + block_size - 1 > other_frame.height')
            self.utils.log(color_by_name("li_red"), debug_prefix, str(other_y + block_size - 1) + '?>' + str(other_frame.height))

            self.controller.exit()

        if this_x < 0 or this_y < 0:
            self.utils.log(color_by_name("li_red"), debug_prefix, 'Negative Input for \"this\" image')
            self.utils.log(color_by_name("li_red"), debug_prefix, 'x' + this_x)
            self.utils.log(color_by_name("li_red"), debug_prefix, 'y' + this_y)

            self.controller.exit()

        if other_x < 0 or other_y < 0:
            self.controller.exit()


    def create_bleeded_image(self, bleed):
        """
        For residuals processing, pixels may or may not exist when trying to create an residual image based
        off the residual blocks, because of padding. This function will make a larger image, and place the same image
        within the larger image, effectively creating a black bleed around the image itself.

        For example, pretend the series of 1's is a static image

        111
        111
        111

        And we need to get the top left most block, with image padding of one pixel. However, no pixels exist. So we
        create a bleeded image,

        00000
        01110
        01110
        01110
        00000

        Then we can create a residual image of the top left pixel with a padding of one pixel, which would yield

        000
        011
        011

        """

        shape = self.frame.shape
        x = shape[0] + bleed + bleed
        y = shape[1] + bleed + bleed
        out_image = np.zeros([x, y, 3], dtype=np.uint8)
        self.copy_from(self.frame, out_image, (0, 0), (bleed, bleed), (shape[0] + bleed - 1, shape[1] + bleed - 1))

        im_out = Frame(self.context, self.utils, self.controller)
        im_out.frame = out_image
        im_out.width = out_image.shape[1]
        im_out.height = out_image.shape[0]

        return im_out

    def mean(self, other):
        return numpy.mean((self.frame - other.frame) ** 2)

        