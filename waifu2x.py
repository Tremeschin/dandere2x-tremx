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
import cv2
import os


color = rgb(255, 200, 10)


class Waifu2x():

    def __init__(self, context, utils, controller, frame):
        self.context = context
        self.utils = utils
        self.controller = controller
        self.frame = frame(self.context, self.utils, self.controller)

        self.waifu2x = None

    # Set internal self.waifu2x to a specific wrapper based on the os and w2x selected
    def set_corresponding(self):

        debug_prefix = "[Waifu2x.set_corresponding]"

        c = fg.li_magenta  # Print this color only in this class

        self.utils.log(c, debug_prefix, "According to the following, ...")

        self.utils.log(c, self.context.indentation, "OS: " + self.context.os)
        self.utils.log(c, self.context.indentation, "Waifu2x: " + self.context.waifu2x_type)

        # Build a string that specifies our os and w2x type
        option = "%s-%s" % (self.context.os, self.context.waifu2x_type)

        # Hacky switch case statement, tho we do instantiate them that's why
        # we define a init instead of a __init__ function
        self.waifu2x = {

            "linux-vulkan":   Waifu2xVulkan(),
            "linux-cpp":      Waifu2xCPP(),

            "windows-vulkan": Waifu2xVulkan(),
            "windows-cpp":    Waifu2xCPP(),

            "windows-caffe":  Waifu2xWindowsCaffe(),

            "linux-fake":     NotFakeWaifu2x(),
            "windows-fake":   NotFakeWaifu2x()

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

    def get_residual_upscaled_file_path_output_frame_number(self, frame_number):
        return self.waifu2x.get_residual_upscaled_file_path_output_frame_number(frame_number)

    def ruthless_residual_eliminator(self):

        debug_prefix = "[Waifu2x.ruthless_residual_eliminator]"

        while not self.controller.stop:
            for residual in os.scandir(self.context.residual):

                residual_path = residual.path
                residual_filename = residual.name

                residual_number = self.utils.get_first_number_of_string(residual_filename)
                upscaled_path = self.get_residual_upscaled_file_path_output_frame_number(residual_number)

                if ( (self.context.last_processing_frame - residual_number) > self.context.safety_ruthless_residual_eliminator_range ):
                    self.utils.log(color, debug_prefix, "Residual number [%s] exists in residual dir and is out of bound, deleting" % residual_number)

                    #print(residual_path)
                    #print(upscaled_path)

                    self.utils.delete_file(residual_path)
                    self.utils.delete_file(upscaled_path)


            for upscaled in os.scandir(self.context.upscaled):

                upscaled_path = upscaled.path
                upscaled_filename = upscaled.name

                upscaled_number = self.utils.get_first_number_of_string(upscaled_filename)

                equivalent_residual = self.context.residual + "residual_%s.jpg" % self.utils.pad_zeros(upscaled_number)
                equivalent_residual_number = self.utils.get_first_number_of_string(equivalent_residual)

                if os.path.isfile(equivalent_residual):

                    if self.frame.is_valid_image(upscaled_path):

                        if ( (self.context.last_processing_frame - equivalent_residual_number) > self.context.safety_ruthless_residual_eliminator_range ):
                            self.utils.log(color, debug_prefix, "Deleting equivalent residual as upscale already exists: [%s]" % equivalent_residual)
                            self.utils.delete_file(equivalent_residual)
                    else:
                        self.utils.log(color, debug_prefix, "[FAILSAFE] Partial saved or corrupted (?) upscaled image: [%s]" % upscaled_path)


                if ( (self.context.last_processing_frame - upscaled_number) > self.context.safety_ruthless_residual_eliminator_range ):

                    if os.path.isfile(upscaled_path):

                        self.utils.log(color, debug_prefix, "Deleting upscaled as passed safety limit [%s]" % upscaled_path)
                        self.utils.delete_file(upscaled_path)

            time.sleep(0.05)


# Welp, only upscales the file by 2x with traditional algorithms
class NotFakeWaifu2x():
    def init(self, context, utils, controller):

        self.context = context
        self.utils = utils
        self.controller = controller

        debug_prefix = "[NotFakeWaifu2x.__init__]"

        self.utils.log(color, debug_prefix, "Will use this \"Waifu2x\" wrapper")

    def verify(self):
        pass

    def generate_run_command(self):
        pass

    def keep_upscaling(self, input_path, output_path):

        while not self.controller.stop:
            if len(os.listdir(input_path)) > 0:
                for file in os.listdir(input_path):

                    try:
                        input = input_path + file
                        output = output_path + file  #.replace(".jpg", ".jpg.png")

                        img = cv2.imread(input)

                        scale_percent = 200  # percent of original size

                        width = int(img.shape[1] * scale_percent / 100)
                        height = int(img.shape[0] * scale_percent / 100)

                        dim = (width, height)

                        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

                        cv2.imwrite(output, resized)

                        #self.utils.delete_file(output)
                        #self.utils.delete_file(input)

                    except Exception:
                        pass

            time.sleep(self.context.waifu2x_wait_for_residuals)

    # Each Waifu2x outputs the images in a different naming sadly
    def get_residual_upscaled_file_path_output_frame_number(self, frame_number):
        return self.context.upscaled + "residual_" + self.utils.pad_zeros(frame_number) + ".jpg"


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Both OS working Waifu2x wrappers

# # For verifying waifu2x binary is in path:

#   Linux:
# bash: type: waifu2x-ncnn-vulkan is /usr/bin/waifu2x-ncnn-vulkan
# bash: type: waifu2x-ncnn-vulka: not found
# 
#   Windows:
# Search through externals/**


# Waifu2x Vulkan (ncnn) wrapper
class Waifu2xVulkan():

    def init(self, context, utils, controller):

        self.context = context
        self.utils = utils
        self.controller = controller

        debug_prefix = "[Waifu2xVulkan.__init__]"

        self.utils.log(color, debug_prefix, "Will use this Waifu2x wrapper")

    # Get the binary if it exist
    def verify(self):

        debug_prefix = "[Waifu2xVulkan.verify]"

        self.utils.log(color, debug_prefix, "Verifying and getting binary")

        self.binary = self.utils.get_binary("waifu2x-ncnn-vulkan")

        self.utils.log(color, debug_prefix, "Got binary: [%s]" % self.binary)

    # Creates the raw command for upscaling a file / directory
    def generate_run_command(self):

        debug_prefix = "[Waifu2xVulkan.generate_run_command]"

        self.utils.log(color, debug_prefix, "Generating run command")

        self.command = [self.binary, "-n", str(self.context.denoise_level), "-t", str(self.context.tile_size), "-j", "4:4:4"]

        # Windows needs the model dirs
        if self.context.os == "windows":
            self.command = self.command + ["-m", os.path.dirname(self.binary) + os.path.sep + self.context.waifu2x_model]

        self.utils.log(color, debug_prefix, "Basic run command is: [\"%s\"]" % self.command)

    # Call the command and upscale a file or directory
    def upscale(self, input_path, output_path):

        debug_prefix = "[Waifu2xVulkan.upscale]"

        # Remove the last / or \
        input_path = input_path[:-1]
        output_path = output_path[:-1]

        # Get a clone of basic usage and extend it based on the I/O
        command = self.command + ["-i", input_path, "-o", output_path]

        if self.context.loglevel >= 3:
            self.utils.log(color, debug_prefix, "Upscaling: [\"%s\"] --> [\"%s\"]" % (input_path, output_path))
            self.utils.log(color, debug_prefix, "Command is %s" % command)

        subprocess = SubprocessUtils("waifu2x-ncnn-vulkan", self.utils)

        subprocess.from_list(command)

        if self.context.os == "windows":
            subprocess.run(working_directory=os.path.dirname(self.binary))

        elif self.context.os == "linux":
            if not self.context.linux_enable_mesa_aco_waifu2x_vulkan:
                subprocess.run()
            else:
                self.utils.log(color, debug_prefix, "Running with RADV_PERFTEST=aco")
                env = os.environ.copy()
                env["RADV_PERFTEST"] = "aco"
                subprocess.run(env=env)

        while subprocess.is_alive():
            time.sleep(0.5)
            if self.controller.stop == True:
                subprocess.terminate()

    # Persistent upscaling
    def keep_upscaling(self, input_path, output_path):

        debug_prefix = "[Waifu2xVulkan.keep_upscaling]"

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

    # Each Waifu2x outputs the images in a different naming sadly
    def get_residual_upscaled_file_path_output_frame_number(self, frame_number):
        return self.context.upscaled + "residual_" + self.utils.pad_zeros(frame_number) + ".jpg.png"


# Waifu2x CPP (converter-cpp) wrapper
class Waifu2xCPP():

    def init(self, context, utils, controller):
        self.context = context
        self.utils = utils
        self.controller = controller

        debug_prefix = "[Waifu2xCPP.__init__]"

        self.utils.log(color, debug_prefix, "Will use this Waifu2x wrapper")

    def verify(self):

        debug_prefix = "[Waifu2xCPP.verify]"

        self.utils.log(color, debug_prefix, "Verifying and getting binary")
        self.binary = self.utils.get_binary("waifu2x-converter-cpp")
        self.utils.log(color, debug_prefix, "Got binary: [%s]" % self.binary)

    # Creates the raw command for upscaling a file / directory
    def generate_run_command(self):

        debug_prefix = "[Waifu2xCPP.generate_run_command]"

        self.utils.log(color, debug_prefix, "Generating run command")

        self.command = [self.binary, "--noise-level", str(self.context.denoise_level), "--block-size", str(self.context.tile_size), "-a", "0", "-j", "16", "-f", "jpg", "-q", "101", "-v", "1"]

        # On the release of CPP looks like only models_rgb was packed
        if self.context.os == "windows":
            self.command = self.command + ["--model-dir", os.path.dirname(self.binary) + os.path.sep + "models_rgb"]

        self.utils.log(color, debug_prefix, "Basic run command is: [\"%s\"]" % self.command)

    # Call the command and upscale a file or directory
    def upscale(self, input_path, output_path):

        debug_prefix = "[Waifu2xCPP.upscale]"

        # Get a clone of basic usage and extend it based on the I/O
        command = self.command + ["-i", input_path[:-1], "-o", output_path[:-1]]

        if self.context.loglevel >= 3:
            self.utils.log(color, debug_prefix, "Upscaling: [\"%s\"] --> [\"%s\"]" % (input_path, output_path))
            self.utils.log(color, debug_prefix, "Command is %s" % command)

        subprocess = SubprocessUtils("waifu2x-converter-cpp", self.utils)

        subprocess.from_list(command)

        if self.context.os == "windows":
            subprocess.run(working_directory=os.path.dirname(self.binary))

        elif self.context.os == "linux":
            subprocess.run()

        while subprocess.is_alive():
            time.sleep(0.5)
            if self.controller.stop == True:
                subprocess.terminate()

    # Persistent upscaling
    def keep_upscaling(self, input_path, output_path):

        debug_prefix = "[Waifu2xCPP.keep_upscaling]"

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

    # Each Waifu2x outputs the images in a different naming sadly
    def get_residual_upscaled_file_path_output_frame_number(self, frame_number):
        return self.context.upscaled + "residual_" + self.utils.pad_zeros(frame_number) + ".jpg"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Windows

# Waifu2x Windows Caffe wrapper [TODO]
class Waifu2xWindowsCaffe():
    def init(self, context, utils, controller):
        self.context = context
        self.utils = utils
        self.controller = controller

        debug_prefix = "[Waifu2xWindowsCaffe.__init__]"

        self.utils.log(color, debug_prefix, "Will use this Waifu2x wrapper")
