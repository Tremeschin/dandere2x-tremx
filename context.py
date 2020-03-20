"""
Context() is likewise a builder in C or C++, it's supposed to
store and make communication between files better
"""

from sty import fg, bg, ef, rs

import sys
import os


color = fg.li_yellow


class Context():

    def __init__(self, utils):

        debug_prefix = "[Context.__init__]"

        self.utils = utils


        # Create context dict
        self.utils.log(color, debug_prefix, "Creating Context dictionary")

        self.context = {}
        self.context["ROOT"] = self.utils.ROOT


        # For absolute-reffering
        self.ROOT = self.utils.ROOT
        self.os = self.utils.get_os()

        self.utils.log(fg.li_red, debug_prefix, "Got operating system: " + self.os)


        # Load up the yaml file        
        self.utils.log(color, debug_prefix, "Loading settings YAML file")

        self.yaml = self.utils.load_yaml(self.ROOT + os.path.sep + "settings.yaml")


        # # # Static Variables # # #
        self.utils.log(color, debug_prefix, "Setting up static variables")


        # Load basic variables
        self.input_file = self.yaml["basic"]["input_file"]
        self.output_file = self.yaml["basic"]["output_file"]


        # Load processing variables
        self.block_size = self.yaml["processing"]["block_size"]
        self.bleed = self.yaml["processing"]["bleed"]


        # "Global" or non-indented options as they're "major"
        self.session_name = self.yaml["session_name"]
        self.waifu2x_type = self.yaml["waifu2x_type"]


        # Create default variables, gotta assign them
        self.resolution = []
        self.valid_resolution = []
        self.fps = None
        self.frame_count = None


        self.utils.log(color, debug_prefix, "Configuring context.* directories")
    
        # Here we name the coresponding context.* directory var and set its "plain form"
        dirs = {
            "residual": "workspace|SESSION|residual",
            "upscaled": "workspace|SESSION|upscaled",
            "iframes": "workspace|SESSION|workspace|iframes"
        }

        self.plain_dirs = []

        

        # This is a really neat way of micromanaging lots of self vars, we basically
        # set the self.$name$ with setattr, not much else is happening here
        for name in dirs:

            # # # Getting the full directory and add it to plain_dirs list # # #

            # Replace SESSION with self.session_name and | with os.path.sep

            dirname = dirs[name]

            replace = {
                '|': os.path.sep,
                'SESSION': self.session_name
            }
            
            for item in replace:
                dirname = dirname.replace(item, replace[item])


            # Build the full dir with replaces syntax
            directory = self.ROOT + os.path.sep + dirname
            self.plain_dirs.append(directory)

            # Set the value
            setattr(self, name, directory)

            self.utils.log(color, "  > self.%s --> %s" % (name, directory))





