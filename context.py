"""
Context() is likewise a builder in C or C++, it's supposed to
store and make communication between files better
"""

from color import *

import sys
import os


color = color_by_name("li_yellow")


class Context():

    def __init__(self, utils):

        debug_prefix = "[Context.__init__]"

        self.utils = utils

        # For absolute-reffering
        self.ROOT = self.utils.ROOT
        self.os = self.utils.get_os()

        self.utils.log(fg.li_red, debug_prefix, "Got operating system: " + self.os)

        # Load up the yaml file        
        self.utils.log(color, debug_prefix, "Loading settings YAML file")

        self.yaml = self.utils.load_yaml(self.ROOT + os.path.sep + "settings.yaml")


        # Global controls, used for stopping d2x's threads
        self.stop = False
        self.debug = self.yaml["developer"]["debug"]


        if self.debug:
            self.utils.log(fg.li_red, debug_prefix, "DEBUG: ON")
        else:
            self.utils.log(fg.li_red, debug_prefix, "DEBUG: OFF")


        # Create context dict
        self.utils.log(color, debug_prefix, "Creating Context dictionary")

        self.context = {}
        self.context["ROOT"] = self.utils.ROOT

        


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
        self.frame_rate = None

        # Resume options, TODO
        self.resume = False


        self.utils.log(color, debug_prefix, "Configuring context.* directories and static files")
    
        # Here we name the coresponding context.* directory var and set its "plain form"
        dirs = {
            "session": "workspace|SESSION",
            "residual": "workspace|SESSION|residual",
            "upscaled": "workspace|SESSION|upscaled",
            "iframes": "workspace|SESSION|workspace|iframes"
        }

        # If we happen to need some static files
        files = {
            "d2x_cpp_out": "workspace|SESSION|plugins_input.d2x",
            "context_vars": "workspace|SESSION|context_vars.yaml" # So CPP can load these vars we set here 
        }

        self.plain_dirs = []
        self.plain_files = []
        

        # This is a really neat way of micromanaging lots of self vars, we basically
        # set the self.$name$ with setattr, not much else is happening here other than
        # replacing SESSION with self.session_name and | with os.path.sep and
        # enumarating both dictionaries to save double the lines of code for dirs and files

        dir_and_file = [("dirs", dirs), ("files", files)]

        for i, reference in enumerate(dir_and_file):
            '''
            print(i, reference)

            0 ('dirs', {'residual': 'wor...
            1 ('files', {'d2x_cpp_ou...

            This way we can have the reference[0] which is the name and reference[1]
            which is the full dictionary
            '''

            name = reference[0]
            dic = reference[1]
        
            for category in dic:

                # # # Getting the full directory and add it to plain_{dirs,files} list # # #

                # Replace our syntax with system-specific one, you'll know
                # seeing the dictionary in the next line:
                
                replace = {
                    '|': os.path.sep,
                    'SESSION': self.session_name
                }

                subname = dic[category] # The "path" itself, with the "|" and "SESSION"
                
                for item in replace:
                    subname = subname.replace(item, replace[item])


                # Build the full dir with replaces syntax
                directory_or_file = self.ROOT + os.path.sep + subname

                if name == "dirs":
                    self.plain_dirs.append(directory_or_file)
                    printname = "directory"

                elif name == "files":
                    self.plain_files.append(directory_or_file)
                    printname = "static files"

                # Set the value based on the "category" -> self.residual, self.upscaled, self.iframes
                setattr(self, category, directory_or_file)

                self.utils.log(color, "  > (%s) self.%s --> %s" % (printname, category, directory_or_file))



    # We save some selected vars for dandere2x_cpp to read them and work
    # properly based on where stuff actually is
    def save_vars(self):

        debug_prefix = "[Context.save_vars]"

        self.utils.log(color, debug_prefix, "Generating data dictionary")

        # Build up the data directory
        data = {
            "residual_dir": self.residual,
            "ROOT": self.ROOT
        }

        self.utils.log(color, debug_prefix, "Saving vars dictionary to YAML file: [%s]" % self.context_vars)

        self.utils.save_yaml(data, self.context_vars)

        self.utils.log(color, debug_prefix, "Saved")

    
    # For resuming TODO
    def load_vars_from_file(self, context_vars_file):
        self.context_data = self.utils.load_yaml(context_vars_file)


