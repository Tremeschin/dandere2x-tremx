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

from color import colors
from PIL import Image
import numpy as np
import imageio
import numpy
import time
import os


color = colors["frame"]


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

        # Basic variables
        self.frame = None
        self.width = None
        self.height = None
        self.name = None

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

            self.utils.log(color, 10, debug_prefix, "Copied from, args = {%s, %s, %s}" % (A_start, B_start, B_end))

        except ValueError as e:
            self.utils.log(colors["error"], 0, debug_prefix, "Fatal error copying block: ", e)
            self.controller.exit()

    # Create and set new frame
    def new(self, width, height):

        debug_prefix = "[Frame.new]"

        self.frame = np.zeros([height, width, 3], dtype=np.uint8)
        self.width = width
        self.height = height
        self.resolution = (width, height)
        self.name = ''
        
        self.utils.log(color, 6, debug_prefix, "Resolution: [%sx%s]" % (width, height))

    # See if can open image, if it's good
    def is_valid_image(self, path):

        debug_prefix = "[Frame.is_valid_image]"

        try:
            # Can we read? True
            imageio.imread(path)
            return True
        except SyntaxError:
            self.utils.log(color, 6, debug_prefix, "[DEBUG] NOT GOOD IMAGE SyntaxError [%s]" % path)
            return False
        except ValueError:
            self.utils.log(color, 6, debug_prefix, "[DEBUG] NOT GOOD IMAGE ValueError [%s]" % path)
            return False

    # Load file based on the filename
    def load_from_path(self, filename):

        debug_prefix = "[Frame.load_from_path]"
        
        self.utils.log(color, 7, debug_prefix, "Name: [%s]" % filename)

        while True:
            try:
                self.frame = imageio.imread(filename).astype(np.uint8)
                #self.frame = numpy.asarray(Image.open(filename))
                break
            except Exception:
                self.utils.log(color, 6, debug_prefix, "Couldn't load image [%s], retrying" % filename)

            if self.controller.stop:
                return 0
            
            # Wait for not hanging this Python GIL
            time.sleep(0.1)

        self.height = self.frame.shape[0]
        self.width = self.frame.shape[1]
        self.resolution = (self.width, self.height)
        self.name = filename

        self.utils.log(color, 7, debug_prefix, "Resolution: [%sx%s]" % (self.width, self.height))

    # Wait on a file if it does not exist yet. Wait can be cancelled via a cancellation token
    def load_from_path_wait(self, filename):

        debug_prefix = "[Frame.load_from_path_wait]"

        self.utils.log(color, 7, debug_prefix, "Waiting for: [%s]" % filename)

        # Wait until the file exists (if ever lol)
        self.utils.until_exist(filename)

        # We can have a false alarm that it exists, but controller.stop could became True
        if not self.controller.stop:
            self.load_from_path(filename)
        else:
            self.utils.log(color, 1, debug_prefix, "Will not load waited file [%s] as controller stopped" % filename)

    # Save an image with specific instructions depending on it's extension type.
    # This saves the image into a .temp until they are fully saved and rename to the original name
    def save(self, directory):

        debug_prefix = "[Frame.save]"

        # Get the file extension
        extension = os.path.splitext(os.path.basename(directory))[1]

        self.utils.log(color, 7, debug_prefix, "Saving to file: [%s], extension is: [%s]" % (directory, extension))

        # Routine on saving to temp file and renaming back at max quality
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

    # Gets the (other_frame), (self.frame), and set to this (self.frame) the other's (self.frame)
    def duplicate(self, other_frame):
        """
        Copy another image into this image using the self.copy_from numpy command. It seems that numpy affects
        the RGB contents of an image, so when another image needs to be copied, rather than copying the file itself,
        load it into a Frame, copy the Frame, then save the Frame, as opposed to copying the file itself.

        This ensure the images stay consistent temporally.
        """

        debug_prefix = "[Frame.duplicate]"

        self.utils.log(color, 6, debug_prefix, "Duplicating from other_frame")

        height_matches = self.height == other_frame.height
        width_matches = self.width == other_frame.width

        # Checks if both height and width matches and if not log the info on what went wrong, exit Dandere2x
        if not height_matches or not width_matches:
            self.utils.log(colors["error"], 0, debug_prefix, "Copy images are not equal")

            errormessage = "Width matches: [%s], Height matches: [%s]" % (width_matches, height_matches)
            errormessage += " | This res: [%sx%s], Other res: [%sx%s]" % (self.width, self.height, other_frame.width, other_frame.height)

            self.utils.log(colors["error"], 0, debug_prefix, errormessage)

            self.controller.exit()

        self.copy_from(other_frame.frame, self.frame, (0, 0), (0, 0), (other_frame.frame.shape[0], other_frame.frame.shape[1]))


if __name__ == "__main__":
    from utils import Miscellaneous
    Miscellaneous()
    print("You shouldn't be running this file directly, Dandere2x is class based and those are handled by dandere2x.py which is controlled by dandere2x_cli.py or the upcoming GUI")
