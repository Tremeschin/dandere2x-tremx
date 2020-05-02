"""
===============================================================================

Purpose: Python wrappers for using Waifu2x independent of the OS

Main wrapper Waifu2x gets the according Waifu2x class based on OS and Context()
set Waifu2x type and abstracts their functions acting as a global wrapper

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
from color import rgb, fg

import time
import os


color = rgb(255, 200, 10)


class Waifu2x():

    def __init__(self, context, utils, controller):
        self.context = context
        self.utils = utils
        self.controller = controller

        self.waifu2x = None


    # Set internal self.waifu2x to a specific wrapper based on the os and w2x selected
    def set_corresponding(self):

        debug_prefix = "[Waifu2x.set_corresponding]"

        c = fg.li_magenta # Print this color only in this class

        self.utils.log(c, debug_prefix, "According to the following, ...")

        self.utils.log(c, self.context.indentation, "OS: " + self.context.os)
        self.utils.log(c, self.context.indentation, "Waifu2x: " + self.context.waifu2x_type)

        # Build a string that specifies our os and w2x type
        option = "%s-%s" % (self.context.os, self.context.waifu2x_type)

        # Hacky switch case statement, tho we do instantiate them that's why
        # we define a init instead of a __init__ function
        self.waifu2x = {
            "linux-vulkan":   Waifu2xLinuxVulkan(),
            "linux-cpp":      Waifu2xLinuxCPP(),
            "windows-vulkan": Waifu2xWindowsVulkan(),
            "windows-cpp":    Waifu2xWindowsVulkan(),
            "windows-caffe":  Waifu2xWindowsCaffe()
        }.get(option, "not_found")

        if self.waifu2x == "not_found":
            self.utils.log(c, debug_prefix, "Chosen waifu2x and or OS not found: [%s]" % option)

        self.waifu2x.init(self.context, self.utils, self.controller)

    def verify(self):
        self.waifu2x.verify()

    def generate_run_command(self):
        self.waifu2x.generate_run_command()

    def upscale(self, input_path, output_path):
        self.waifu2x.upscale(input_path, output_path)

    def keep_upscaling(self, input_path, output_path):
        self.waifu2x.keep_upscaling(input_path, output_path)





# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Linux


# # For verifying waifu2x binary is in path:

# bash: type: waifu2x-ncnn-vulkan is /usr/bin/waifu2x-ncnn-vulkan
# bash: type: waifu2x-ncnn-vulka: not found
# [TODO]: This only finds waifu2x's in PATH]



# Waifu2x Linux Vulkan (ncnn) wrapper
class Waifu2xLinuxVulkan():

    def init(self, context, utils, controller):

        self.context = context
        self.utils = utils
        self.controller = controller

        debug_prefix = "[Waifu2xLinuxVulkan.__init__]"

        self.utils.log(color, debug_prefix, "Will use this Waifu2x wrapper")


    # Get the binary if it exist
    def verify(self):

        debug_prefix = "[Waifu2xLinuxVulkan.verify]"

        self.utils.log(color, debug_prefix, "Verifying and getting binary")

        self.binary = self.utils.get_binary("waifu2x-ncnn-vulkan")

        self.utils.log(color, debug_prefix, "Got binary: [%s]" % self.binary)


    # Creates the raw command for upscaling a file / directory
    def generate_run_command(self):

        debug_prefix = "[Waifu2xLinuxVulkan.generate_run_command]"

        self.utils.log(color, debug_prefix, "Generating run command")

        self.command = [self.binary, "-n", str(self.context.denoise_level), "-t", str(self.context.tile_size)]

        self.utils.log(color, debug_prefix, "Basic run command is: [\"%s\"]" % self.command)


    # Call the command and upscale a file or directory
    def upscale(self, input_path, output_path):

        debug_prefix = "[Waifu2xLinuxVulkan.upscale]"

        # Get a clone of basic usage and extend it based on the I/O
        command = self.command + ["-i", input_path, "-o", output_path]

        if self.context.loglevel >= 3:
            self.utils.log(color, debug_prefix, "Upscaling: [\"%s\"] --> [\"%s\"]" % (input_path, output_path))
            self.utils.log(color, debug_prefix, "Command is %s" % command)

        subprocess = SubprocessUtils("waifu2x-ncnn-vulkan", self.utils)

        subprocess.from_list(command)

        subprocess.run()

        while subprocess.is_alive():
            time.sleep(0.5)
            if self.controller.stop is True:
                subprocess.terminate()




    # Persistent upscaling
    def keep_upscaling(self, input_path, output_path):

        debug_prefix = "[Waifu2xLinuxVulkan.keep_upscaling]"

        self.utils.log(color, debug_prefix, "Keep upscaling: [\"%s\"] --> [\"%s\"]" % (input_path, output_path))

        # If we get a message to stop (ie. finished or panic)
        while not self.controller.stop:

            # See if there is any file to upscale
            if len(os.listdir(input_path)) > 0:
                self.upscale(input_path, output_path)

                if self.context.loglevel >= 3:
                    self.utils.log(color, debug_prefix, "Upscaled everything, looping again..")
            else:
                if self.context.loglevel >= 3:
                    self.utils.log(color, debug_prefix, "Input [\"%s\"] is empty" % input_path)

            # Do not call it
            time.sleep(self.context.waifu2x_wait_for_residuals)

        self.utils.log(color, debug_prefix, "Exiting waifu2x keep upscaling")


# Waifu2x Linux CPP (converter-cpp) wrapper
class Waifu2xLinuxCPP():

    def init(self, context, utils, controller):
        self.context = context
        self.utils = utils
        self.controller = controller

        debug_prefix = "[Waifu2xLinuxCPP.__init__]"

        self.utils.log(color, debug_prefix, "Will use this Waifu2x wrapper")


    def verify(self):

        debug_prefix = "[Waifu2xLinuxCPP.verify]"

        self.utils.log(color, debug_prefix, "Verifying and getting binary")

        self.binary = self.utils.get_binary("waifu2x-converter-cpp")

        self.utils.log(color, debug_prefix, "Got binary: [%s]" % self.binary)






# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Windows


# Waifu2x Windows Vulkan (ncnn) wrapper
class Waifu2xWindowsVulkan():
    def init(self, context, utils, controller):
        self.context = context
        self.utils = utils
        self.controller = controller

        debug_prefix = "[Waifu2xWindowsVulkan.__init__]"

        self.utils.log(color, debug_prefix, "Will use this Waifu2x wrapper")


# Waifu2x Windows CPP (converter-cpp) wrapper
class Waifu2xWindowsCPP():
    def init(self, context, utils, controller):
        self.context = context
        self.utils = utils
        self.controller = controller

        debug_prefix = "[Waifu2xWindowsCPP.__init__]"

        self.utils.log(color, debug_prefix, "Will use this Waifu2x wrapper")


# Waifu2x Windows Caffe wrapper
class Waifu2xWindowsCaffe():
    def init(self, context, utils, controller):
        self.context = context
        self.utils = utils
        self.controller = controller

        debug_prefix = "[Waifu2xWindowsCaffe.__init__]"

        self.utils.log(color, debug_prefix, "Will use this Waifu2x wrapper")
