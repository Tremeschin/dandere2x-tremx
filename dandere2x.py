"""
===============================================================================

        Dandere2x - Fast Waifu2x Upscale!!

Purpose: The most abstract script, deals with connecting all the others

Creates all the classes we need, checks, verifies, connects them, setup
and run Dandere2x. 

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

from vp import VapourSynthWrapper
from processing import Processing
from controller import Controller
from d2xmath import D2XMath
from plugins import Plugins
from context import Context
from waifu2x import Waifu2x
from core import CoreLoop
from frame import Frame
from video import Video
from utils import Utils

import argparse
import time
import os


color = rgb(200, 255, 80)
phasescolor = rgb(84, 255, 87)
ROOT = os.path.dirname(os.path.abspath(__file__))


class Dandere2x():

    def __init__(self, args):
        self.args = args
        

    # This function loads up the "core" variables and objects
    def load(self):

        debug_prefix = "[Dandere2x.load]"

        self.utils = Utils()

        self.utils.log(phasescolor, "# # [Load phase] # #")
        self.utils.log(color, debug_prefix, "Created Utils()")

        # Communication between files, static
        self.utils.log(color, debug_prefix, "Creating Context()")
        self.context = Context(self.utils)

        # Communication between files, depends on runtime
        self.utils.log(color, debug_prefix, "Creating Controller()")
        self.controller = Controller()

        # Let Utils access Controller
        self.utils.log(color, debug_prefix, "Giving Utils, Controller")
        self.utils.set_controller(self.controller)

        # Let Utils access Context
        self.utils.log(color, debug_prefix, "Giving Utils, Context")
        self.utils.set_context(self.context)

        # Deals with Video related stuff
        self.utils.log(color, debug_prefix, "Creating Video()")
        self.video = Video(self.context, self.utils, self.controller)

        # "Layers" of processing before the actual upscale from Waifu2x
        self.utils.log(color, debug_prefix, "Creating Plugins()")
        self.plugins = Plugins(self.context, self.utils, self.controller)

        # Our upscale wrapper, on which the default is Waifu2x
        self.utils.log(color, debug_prefix, "Creating Waifu2x()")
        self.waifu2x = Waifu2x(self.context, self.utils, self.controller)

        # Deals with Plugins
        self.utils.log(color, debug_prefix, "Creating Processing()")
        self.processing = Processing(self.context, self.utils, self.controller)
        
        # Math utils, specific cases for Dandere2x
        self.utils.log(color, debug_prefix, "Creating D2XMath()")
        self.math = D2XMath(self.context, self.utils)

        # On where everything is controlled and starts
        self.utils.log(color, debug_prefix, "Creating CoreLoop()")
        self.core = CoreLoop(self.context, self.utils, self.controller, self.plugins, self.waifu2x)

        # Deals with images, mostly numpy wrapper and special functions like block substitution
        self.utils.log(color, debug_prefix, "Creating Frame()")
        self.frame = Frame(self.context, self.utils, self.controller)
        

        if self.context.use_vapoursynth:
            # Vapoursynth wrapper, optional
            self.utils.log(color, debug_prefix, "Creating VapourSynthWrapper()")
            self.vapoursynth_wrapper = VapourSynthWrapper(self.context, self.utils, self.controller)

            self.vapoursynth_wrapper.apply_filter("transpose", "/home/tremeschin/github/clone/dandere2x-new/input.mkv", "/home/tremeschin/github/clone/dandere2x-new/out.mkv")
            exit()


    # This function mainly configures things before upscaling and verifies stuff,
    # sees if it's a resume session, etc
    def setup(self):

        self.utils.log(phasescolor, "# # [Setup phase] # #")

        debug_prefix = "[Dandere2x.setup]"

        # Set and verify Waifu2x
        self.utils.log(color, debug_prefix, "Setting corresponding Waifu2x")
        self.waifu2x.set_corresponding()

        self.utils.log(color, debug_prefix, "Verifying Waifu2x")
        self.waifu2x.verify()

        self.utils.log(color, debug_prefix, "Generating run command from Waifu2x")
        self.waifu2x.generate_run_command()


        # Check if context_vars file exist and is set to be resume
        # If force argument is set, force not resume session
        if not self.args["force"]:
            self.utils.log(color, debug_prefix, "Checking if is Resume session")
            self.context.resume = self.utils.check_resume()
        else:
            self.utils.log(rgb(255,100,0), debug_prefix, "FORCE MODE ENABLED, FORCING RESUME=FALSE")
            self.context.resume = False


        # NOT RESUME SESSION, delete previous session, load up and check directories
        if not self.context.resume:

            # As we're loading it with non-resume code logic
            self.context.resume = True

            # Log and reset session directory
            self.utils.log(color_by_name("li_red"), debug_prefix, "NOT RESUME SESSION, deleting session [%s]" % self.context.session_name)
            self.utils.reset_dir(self.context.session)

            # Check dirs
            self.utils.log(color, debug_prefix, "Checking directories")
            self.utils.check_dirs()

            # Reset files
            self.utils.log(color, debug_prefix, "Reseting files")
            self.utils.reset_files()

            # Debugging, show static files
            self.utils.log(color, debug_prefix, "Showing static files")
            self.utils.show_static_files()

            # Get video info
            self.utils.log(color, debug_prefix, "Getting video info")
            self.video.get_video_info()

            self.utils.log(color, debug_prefix, "Showing video info")
            self.video.show_info()

            # Set block size and a valid input resolution
            self.utils.log(color, debug_prefix, "Setting block_size")
            self.math.set_block_size()

            self.utils.log(color, debug_prefix, "Getting valid input resolution")
            self.math.get_a_valid_input_resolution()

            # Save vars of context so d2x_cpp can use them and we can resume it later
            self.utils.log(color, debug_prefix, "Saving Context vars to file")
            self.context.save_vars()
        
        
        # IS RESUME SESSION, basically load instructions from the context saved vars
        else: 
            self.utils.log(color_by_name("li_red"), debug_prefix, "IS RESUME SESSION")

            self.utils.log(color, debug_prefix, "Loading Context vars from context_vars file")

            self.context.load_vars_from_file(self.context.context_vars)


    # Here's the core logic for Dandere2x, good luck other files
    def run(self):
        
        debug_prefix = "[Dandere2x.run]"

        self.utils.log(phasescolor, "# # [Run phase] # #")

        self.utils.log(phasescolor, "# # TESTING FRAME() # #")
        frame = Frame(self.context, self.utils, self.controller)
        frame.load_from_path(self.context.ROOT + os.path.sep + "small.png")

        frame2 = Frame(self.context, self.utils, self.controller)
        #frame2.new(1920, 1080)
        frame2.new(272, 207)
        frame2.duplicate(frame)
        
        frame2.save("small_copy.png")

        self.utils.log(phasescolor, "# # END FRAME() # #")

        
        
        self.core.start()
     
        # Simulate exiting
        #self.utils.log(color, debug_prefix, "Simulating exit in 3 seconds")

        #for i in range(3, 0, -1):
        #    self.utils.log(color, debug_prefix, i)
        #    time.sleep(1)


        #self.waifu2x.upscale(self.context.ROOT + "/img.png", self.context.ROOT + "/img2x.png")

        
    
        for i in range(4, 0, -1):
            self.utils.log(color, debug_prefix, i)
            time.sleep(1)


        self.controller.exit()

        for thread in self.context.threads:
            self.utils.log(color, debug_prefix, "Joining thread: [\"%s\"]" % thread)
            self.context.threads[thread].join()
        


if __name__ == "__main__":

    # Create ArgumentParser
    args = argparse.ArgumentParser(description='Optional arguments for Dandere2x')

    # # Arguments

    # Force deletion of session, don't resume
    args.add_argument('-f', '--force', required=False, action="store_true", help="Forces deletion of session")
    
    # Parse args and make dictionary
    args = args.parse_args()

    args = {
        "force": args.force
    }

    # Run Dandere2x

    d2x = Dandere2x(args)
    d2x.load()
    d2x.setup()
    d2x.run()
