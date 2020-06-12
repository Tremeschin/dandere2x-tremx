"""
===============================================================================

Purpose: Python wrappers for using Upscaler independent of the OS

Main wrapper Upscaler gets the according Upscaler class based on OS and Context()
set Upscaler type and abstracts their functions acting as a global wrapper

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
from color import colors
import time
import cv2
import os


color = colors["upscaler"]


# This upsed to be a lot of separate classes though a single one was really doable
# Just pay attention on the code flow because some upscalers act different
class Upscaler():

    def __init__(self, context, utils, controller, frame):
        self.context = context
        self.utils = utils
        self.controller = controller
        self.frame = frame(self.context, self.utils, self.controller)

        self.type = self.context.upscaler_type

        # Show info
        self.utils.log(colors["li_magenta"], 3, self.context.indentation, "OS: " + self.context.os)
        self.utils.log(colors["li_magenta"], 3, self.context.indentation, "Upscaler: " + self.type)

    # Get the binary, "verify" it exists, is present
    def verify(self):
        
        debug_prefix = "[Upscaler.verify]"

        self.utils.log(color, 3, debug_prefix, "Verifying and getting binary")

        types_binary = {
            "waifu2x-ncnn-vulkan": "waifu2x-ncnn-vulkan",
            "waifu2x-converter-cpp": "waifu2x-converter-cpp",
            "srmd-ncnn-vulkan": "srmd-ncnn-vulkan",
            "realsr-ncnn-vulkan": "realsr-ncnn-vulkan",
            "fake": None
        }

        # The filename of binary we're going to search
        search_binary = types_binary[self.context.upscaler_type]

        if not search_binary == None:

            self.binary = self.utils.get_binary(search_binary)

            if self.binary == None:
                self.utils.log(colors["error"], 0, debug_prefix, "UPSCALER BINARY NOT FOUND IN EXTERNALS")

            self.utils.log(color, 1, debug_prefix, "Got binary: [%s]" % self.binary)

            self.binary_filename = self.utils.get_basename(self.binary)
            self.utils.log(color, 1, debug_prefix, "Got binary filename: [%s]" % self.binary_filename)

            # Where the binary is located, for getting necessary dlls and libraries
            # It's the cwd or working directory of the upscaler subprocess
            self.working_directory = os.path.dirname(self.binary)
            self.utils.log(color, 2, debug_prefix, "Working directory is [%s]" % self.working_directory)

        else:
            self.binary = None

    # This generates the run command without the input and output arguments
    def generate_run_command(self):

        debug_prefix = "[Upscaler.generate_run_command]"

        self.utils.log(color, 4, debug_prefix, "Generating run command")

        # None is the "fake" upscaler
        if not self.binary == None:

            # Start the command with only calling the binary
            self.command = [self.binary_filename]

            # nihui's upscalers have the same arguments
            if self.type in ["waifu2x-ncnn-vulkan", "srmd-ncnn-vulkan", "realsr-ncnn-vulkan"]:

                self.command += [
                    "-t", str(self.context.tile_size),
                    "-j", self.context.load_proc_save,
                    "-s", str(self.context.upscale_ratio)
                ]

                # realsr-ncnn-vulkan doesn't have a denoiser
                if not self.type == "realsr-ncnn-vulkan":
                    self.command += ["-n", str(self.context.denoise_level)]

            # Waifu2x C++ arguments are a bit different
            elif self.type == "waifu2x-converter-cpp":

                self.command += [
                    "--noise-level", str(self.context.denoise_level),
                    "--block-size", str(self.context.tile_size),
                    "--scale-ratio", str(self.context.upscale_ratio),
                    "-a", "0",
                    "-j", "4",
                    "-f", "jpg",
                    "-q", "101",
                    "-v", "1"
                ]

                # I'm not sure how good "-j" (jobs) are for the C++ so I'll let you decide
                if not self.context.w2x_converter_cpp_jobs == None:
                    self.command += ["-j", self.context.w2x_converter_cpp_jobs]

                # TODO: Is this necessary to make Waifu2x C++ work?
                if self.context.os == "windows" and self.type == "waifu2x-converter-cpp":
                    self.command = self.command + ["--model-dir", os.path.dirname(self.binary) + os.path.sep + "models_rgb"]

            # Set the model of the upscaler if one is set, TODO: C++ only has that one?
            if not self.context.upscaler_model == None and not self.type == "waifu2x-converter-cpp":

                # Windows releases has the models under the release folder
                if self.context.os == "windows":
                    model = self.working_directory + os.path.sep + self.context.upscaler_model
                
                # Linux should be able to figure it out based on the working directory and PATH (?)
                elif self.context.os == "linux":
                    model = self.context.upscaler_model

                # Add the model path
                self.command = self.command + ["-m", model]

            self.utils.log(color, 5, debug_prefix, "Basic run command is: [\"%s\"]" % self.command)

    # Upscale this input to this output, usually directories as argument
    def upscale(self, input_path, output_path):
        
        debug_prefix = "[Upscaler.upscale]"

        # Remove the last / or \
        input_path = input_path[:-1]
        output_path = output_path[:-1]

        # Get a clone of basic usage and extend it based on the I/O
        command = self.command + ["-i", input_path, "-o", output_path]
        
        # Verbose logging
        self.utils.log(color, 4, debug_prefix, "Upscaling: [\"%s\"] --> [\"%s\"]" % (input_path, output_path))
        self.utils.log(color, 5, debug_prefix, "Command is %s" % command)

        # Create a SubprocessUtils that wraps Python's subprocess
        upscaler_subprocess = SubprocessUtils(self.type, self.utils, self.context)

        # Build the subprocess from the self.command list with the input and output arguments
        upscaler_subprocess.from_list(command)

        # Copy the environment, compatibility purposes
        env = os.environ.copy()

        # Linux AMD GPUs is preferred RADV_PERFTEST=aco var as it speeds Vulkan performance a lot
        if self.context.os == "linux":
            if self.context.linux_enable_mesa_aco_upscaler:
                env["RADV_PERFTEST"] = "aco"

        # Failsafe Windows executing the upscaler?
        if self.context.os == "windows":
            os.chdir(self.working_directory)

            # Was more stable..? not really optimal but welp
            shell = True
        else:
            shell = False
        
        # Run the subprocess with the working directory and envs we've set
        upscaler_subprocess.run(working_directory=self.working_directory, env=env, shell=shell)

        # Wait until its process finishes or controller says to stop
        while upscaler_subprocess.is_alive():
            time.sleep(0.1)
            if self.controller.stop == True:
                upscaler_subprocess.terminate()

    # Keep upscaling until Dandere2x says Controller to stop or we had finished
    def keep_upscaling(self, input_path, output_path):
        
        debug_prefix = "[Upscaler.keep_upscaling]"

        # "Fake" upscaler just for testing raw Dandere2x Python performance
        if not self.type == "fake":

            self.utils.log(color, 1, debug_prefix, "Keep upscaling: [\"%s\"] --> [\"%s\"]" % (input_path, output_path))

            # If we get a message to stop (ie. finished or panic)
            while not self.controller.stop:

                # See if there is any file to upscale
                if len(os.listdir(input_path)) > 0:
                    self.upscale(input_path, output_path)
                    self.utils.log(color, 5, debug_prefix, "Upscaled everything, looping again..")
                else:
                    self.utils.log(color, 8, debug_prefix, "Input [\"%s\"] is empty" % input_path)

                # Do not call it, otherwise would spam too much
                time.sleep(self.context.upscaler_wait_for_residuals)

            self.utils.log(color, 1, debug_prefix, "Exiting upscaler keep upscaling")
        
        # "Fake" upscaler code
        else:
            # While Dandere2x is running / needs upscaling residuals
            while not self.controller.stop:
                
                # If the input dir is not empty
                if len(os.listdir(input_path)) > 0:

                    # For each file in the input directory
                    for residual_file in os.listdir(input_path):
                        
                        # There can be errors loading / saving so better ignore them
                        try:
                            # Routine to upscale a image using cv2 by context.upscale_ratio
                            residual_input = input_path + residual_file
                            output = output_path + residual_file
                            img = cv2.imread(residual_input)
                            scale_percent = self.context.upscale_ratio*100  # percent of original size
                            width = int(img.shape[1] * scale_percent / 100)
                            height = int(img.shape[0] * scale_percent / 100)
                            dim = (width, height)
                            resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
                            cv2.imwrite(output, resized)
                        except Exception:
                            pass
                
                # Wait, otherwise would spam too much
                time.sleep(self.context.upscaler_wait_for_residuals)

    # Get the expected output of the upscaled residual filename
    def get_residual_upscaled_file_path_output_frame_number(self, frame_number):

        if self.type in ["waifu2x-ncnn-vulkan", "srmd-ncnn-vulkan", "realsr-ncnn-vulkan"]:
            return self.context.upscaled + "residual_" + self.utils.pad_zeros(frame_number) + ".jpg.png"
            
        if self.type in ["waifu2x-converter-cpp", "fake"]:
            return self.context.upscaled + "residual_" + self.utils.pad_zeros(frame_number) + ".jpg"

    # Delete residuals that have been upscaled and upscaled residuals that are already used
    def ruthless_residual_eliminator(self):
        
        debug_prefix = "[Upscaler.ruthless_residual_eliminator]"

        self.utils.log(color, 6, debug_prefix, "Alive!")

        # While Dandere2x is running
        while not self.controller.stop:
            
            # # Deal with residuals images
            for residual in os.scandir(self.context.residual):

                # Get the absolute path of the file as well its filename
                residual_path = residual.path
                residual_filename = residual.name

                # Get the frame number of that residual
                residual_number = self.utils.get_first_number_of_string(residual_filename)

                # Get the upscaled path of the corresponding residual number
                upscaled_path = self.get_residual_upscaled_file_path_output_frame_number(residual_number)

                # If the [(current processing frame) - (this residual number)] > threshold:
                #    Delete the residual and upscaled
                #
                # This is because both files are out of bounds
                if ( (self.context.last_processing_frame - residual_number) > self.context.safety_ruthless_residual_eliminator_range ):
                    
                    self.utils.log(color, 6, debug_prefix, "Residual number [%s] exists in residual dir and is out of bound, deleting" % residual_number)

                    # Delete both residual and upscaled files that are out of bounds
                    self.utils.delete_file(residual_path)
                    self.utils.delete_file(upscaled_path)

            # # Deal with the upscaled residual images
            for upscaled in os.scandir(self.context.upscaled):

                # Get the absolute path of the file as well its filename
                upscaled_path = upscaled.path
                upscaled_filename = upscaled.name

                # Get the frame number of that upscaled
                upscaled_number = self.utils.get_first_number_of_string(upscaled_filename)

                # Get the equivalent residual path of this upscaled residual
                equivalent_residual = self.context.residual + "residual_%s.jpg" % self.utils.pad_zeros(upscaled_number)

                # If the residual even exists at first hand
                if os.path.isfile(equivalent_residual):

                    # Checking if is upscaled is a valid path is to make sure those files have been saved properly on disk
                    if self.frame.is_valid_image(upscaled_path):

                        # Delete the equivalent residual as upscaled exists and is valid image
                        self.utils.delete_file(equivalent_residual)

                        self.utils.log(color, 6, debug_prefix, "Deleting equivalent residual as upscale already exists and is valid image: [%s]" % equivalent_residual)
                    else:
                        self.utils.log(color, 6, debug_prefix, "[FAILSAFE] Partial saved or corrupted (?) upscaled image: [%s]" % upscaled_path)

                # If the [(current processing frame) - (this upscaled number)] > threshold:
                #    Delete the upscaled
                #
                # This is because the upscaled file is out of bounds comparing to current processing frame
                if ( (self.context.last_processing_frame - upscaled_number) > self.context.safety_ruthless_residual_eliminator_range ):
                    self.utils.log(color, 6, debug_prefix, "Deleting upscaled as passed safety limit [%s]" % upscaled_path)
                    self.utils.delete_file(upscaled_path)

            # Let something happen
            time.sleep(0.05)


if __name__ == "__main__":
    from utils import Miscellaneous
    print("You shouldn't be running this file directly, Dandere2x is class based and those are handled by dandere2x.py which is controlled by dandere2x_cli.py or a gui")
