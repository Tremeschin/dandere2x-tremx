# main wrapper, abstracts everything else

from sty import fg, bg, ef, rs

from processing import Processing
from d2xmath import D2XMath
from plugins import Plugins
from context import Context
from waifu2x import Waifu2x
from core import CoreLoop
from video import Video
from utils import Utils

import os


color = fg(200, 255, 80)
ROOT = os.path.dirname(os.path.abspath(__file__))


class Dandere2x():
    def __init__(self):

        debug_prefix = "[Dandere2x.__init__]"

        self.utils = Utils()

        self.utils.log(color,  "\n # # [Welcome to Dandere2x] # #\n")
        self.utils.log(color, debug_prefix, "Created Utils()")

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
        self.core = CoreLoop(self.context, self.utils)
        


        
        # # # Here's the core logic for Dandere2x # # #

        # Set and verify Waifu2x
        self.waifu2x.set_corresponding_verify()

        # Check dirs
        self.utils.log(color, debug_prefix, "Checking directories")
        self.utils.check_dirs()

        # Debugging, show static files
        self.utils.log(color, debug_prefix, "Showing static files")
        self.utils.show_static_files()


        # Get video info
        self.utils.log(color, debug_prefix, "Getting video info")
        self.video.video_info()

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

        # Save vars of context so d2x_cpp can use them
        self.utils.log(color, debug_prefix, "Saving Context vars to file")
        self.context.save_vars()

        self.core.start()

        

        
        


Dandere2x()

