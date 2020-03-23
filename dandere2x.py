# main wrapper, abstracts everything else

from color import *

from processing import Processing
from d2xmath import D2XMath
from plugins import Plugins
from context import Context
from waifu2x import Waifu2x
from core import CoreLoop
from video import Video
from utils import Utils

import os


color = rgb(200, 255, 80)
ROOT = os.path.dirname(os.path.abspath(__file__))


class Dandere2x():

    def __init__(self):

        debug_prefix = "[Dandere2x.__init__]"
        
        self.utils = Utils()
        self.utils.log(color, debug_prefix, "Created Utils()")


    # This function loads up the "core" variables and objects
    def load(self):

        self.utils.log(color,  "\n # # [Load phase] # #\n")

        debug_prefix = "[Dandere2x.load]"
        
        self.utils.log(color, debug_prefix, "Creating Context()")
        self.context = Context(self.utils)

        self.utils.log(color, debug_prefix, "Giving Utils, Context")
        self.utils.set_context(self.context)

        self.utils.log(color, debug_prefix, "Creating Video()")
        self.video = Video(self.context, self.utils)

        self.utils.log(color, debug_prefix, "Creating Plugins()")
        self.plugins = Plugins(self.context, self.utils)

        self.utils.log(color, debug_prefix, "Creating Waifu2x()")
        self.waifu2x = Waifu2x(self.context, self.utils)

        self.utils.log(color, debug_prefix, "Creating Processing()")
        self.processing = Processing(self.context, self.utils)
        
        self.utils.log(color, debug_prefix, "Creating D2XMath()")
        self.math = D2XMath(self.context, self.utils)

        self.utils.log(color, debug_prefix, "Creating CoreLoop()")
        self.core = CoreLoop(self.context, self.utils, self.plugins)
        

    # This function mainly configures things before upscaling and verifies stuff
    def setup(self):

        self.utils.log(color,  "\n # # [Setup phase] # #\n")

        debug_prefix = "[Dandere2x.setup]"

        # Set and verify Waifu2x
        self.utils.log(color, debug_prefix, "Getting n' Verifying Waifu2x")
        self.waifu2x.set_corresponding_verify()


        # NOT RESUME SESSION, delete previous session, load up and check directories
        if not self.context.resume:

            # Log and reset session directory
            self.utils.log(fg.li_red, debug_prefix, "NOT RESUME SESSION, deleting session [%s]" % self.context.session_name)
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

            # 
            #
            #

            # Save vars of context so d2x_cpp can use them and we can resume it later
            self.utils.log(color, debug_prefix, "Saving Context vars to file")
            self.context.save_vars()
        
        
        # IS RESUME SESSION, basically load instructions from the context saved vars
        else: 
            self.utils.log(fg.li_red, debug_prefix, "IS RESUME SESSION")

            self.context.load_vars_from_file(self.context.context_vars)


    # Here's the core logic for Dandere2x, starts threading and whatnot
    def run(self):

        self.utils.log(color,  "\n # # [Run phase] # #\n")

        self.core.start()


if __name__ == "__main__":
    d2x = Dandere2x()
    d2x.load()
    d2x.setup()
    d2x.run()
