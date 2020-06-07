"""
===============================================================================

Purpose: Utilities to verify if we should continue the session

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
import os


# A class that checks and do some boring stuff 
class FailSafe():

    def __init__(self, utils):
        self.utils = utils

    # Some upscalers only allow 4x, others 1x or 2x, others 2x, 3x, 4x
    # so we gotta make sure we don't go into those pifalls before starting a session
    def compatible_utype_uratio(self, upscaler, uratio):
        
        debug_prefix = "[FailSafe.compatible_utype_uratio]"

        # Upscaling ratio can't be zero or negative, only natural numbers
        # Probably can be floating points with "fake" and "waifu2x-converter-cpp" but rounding errors.....
        if uratio <= 0:
            self.utils.log(colors["li_red"], 0, debug_prefix, "[ERROR] Upscale ratio is zero or negative")
            sys.exit(-1)

        # If not uratio is an integer
        if not int(uratio) == uratio:
            self.utils.log(colors["li_red"], 0, debug_prefix, "[ERROR] Please use a integer upscale_ratio")
            sys.exit(-1)

        # Fake doesn't care about the rations unless
        if upscaler == "fake":
            return

        # The compatible upscale ratios based on the upscalers
        compatible = {
            "waifu2x-ncnn-vulkan": [1, 2],
            "waifu2x-converter-cpp": [1, 2],
            "realsr-ncnn-vulkan": [4],
            "srmd-ncnn-vulkan": [2, 3, 4]
        }

        # Get the one we're going to use
        compatible = compatible[upscaler]

        # Is the selected uratio not in the list? error
        if not uratio in compatible:
            self.utils.log(colors["li_red"], 0, debug_prefix, "[ERROR] Not compatible upscale_ratio with this upscaler, options are:")
            self.utils.log(colors["li_red"], 0, debug_prefix, compatible)
            sys.exit(-1)

    # Some upscalers have wider range of denoising
    def compatible_upscaler_denoise(self, upscaler, denoise):

        debug_prefix = "[FailSafe.compatible_upscaler_denoise]"

        # denoise can't be a floating value
        if not int(denoise) == denoise:
            self.utils.log(colors["li_red"], 0, debug_prefix, "[ERROR] Please use a integer denoise_level")
            sys.exit(-1)

        # dealsr doesn't have a denoiser, we just don't add the argument on upscaler.py
        if upscaler in ["realsr-ncnn-vulkan", "fake"]:
            return

        # The compatible denoise levels based on the upscalers
        # Note that range(a, b) is exclusive on b, ie, range(1, 5) -> [1, 2, 3, 4]
        compatible = {
            "waifu2x-ncnn-vulkan": [x for x in range(-1, 4)],
            "waifu2x-converter-cpp": [x for x in range(0, 4)],
            "srmd-ncnn-vulkan": [x for x in range(-1, 11)]
        }

        # Get the one we're going to use
        compatible = compatible[upscaler]

        # Is the selected denoise not in the list? error
        if not denoise in compatible:
            self.utils.log(colors["li_red"], 0, debug_prefix, "[ERROR] Not compatible denoise with this upscaler, options are:")
            self.utils.log(colors["li_red"], 0, debug_prefix, compatible)
            sys.exit(-1)
        
    # Check if input exists and output directory exists, if not create it
    def check_input_output(self, input_file, output_file):

        debug_prefix = "[FailSafe.check_input_output]"

        # Is the input file even an file? no? error
        if not os.path.isfile(input_file):
            self.utils.log(colors["li_red"], 0, debug_prefix, "[ERROR] Input file is not a file")
            sys.exit(-1)

        # Get the directory the output file was set and check if it exists
        output_basedir = os.path.dirname(output_file)

        # Make directory if it doesn't exist
        self.utils.mkdir_dne(output_basedir)
        
        
if __name__ == "__main__":
    import misc.greeter_message
    print("You shouldn't be running this file directly, Dandere2x is class based and those are handled by dandere2x.py which is controlled by dandere2x_cli.py or a gui")
