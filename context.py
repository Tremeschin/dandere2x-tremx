"""
===============================================================================

Purpose: Class Context() deals with multiple file communications and mostly
"static" variables, or "global constants", think context as in "session settings"

Yes that is very dangerous and not recommended however this works really really
good as basically this class is accessible on almost all Dandere2x Python scripts
files and it's used as a reference on the current state of the program. Also we
save this variables here and load them up when resuming sessions, so it's a way of
making persistent session based variables without much trouble

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


from color import color_by_name, fg, rgb

import sys
import os


color = color_by_name("li_yellow")


class Context():

    def __init__(self, utils):

        self.indentation = "··· |"
        debug_prefix = "[Context.__init__]"

        self.utils = utils

        # Set the (static) rootfolder substitution for changing paths session folders
        self.rootfolder_substitution = "<#ROOTFOLDER#>"
        self.utils.log(color, debug_prefix, "Rootfolder substitution is [%s] on Context and context_vars file" % self.rootfolder_substitution)

        # For absolute-reffering
        self.ROOT = self.utils.ROOT
        self.os = self.utils.get_os()

        self.utils.log(fg.li_red, debug_prefix, "Got operating system: " + self.os)

        # Load up the yaml file        
        self.utils.log(color, debug_prefix, "Loading settings YAML file")

        self.yaml = self.utils.load_yaml(self.ROOT + os.path.sep + "settings.yaml")


        # Global controls, used for stopping d2x's threads
        self.loglevel = self.yaml["developer"]["loglevel"]

        
        self.utils.log(fg.li_red, debug_prefix, "LOGLEVEL: [%s]" % self.loglevel)


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


        # Vapoursynth settings
        self.use_vapoursynth = self.yaml["vapoursynth"]["enabled"]
        self.vapoursynth_pre = self.yaml["vapoursynth"]["pre"]
        self.vapoursynth_pos = self.yaml["vapoursynth"]["pos"]


        # # The special case where the session name is "auto",
        # so we set it according to the input file "a.mkv" -> "a"
        if self.session_name == "auto":
            self.session_name = self.utils.get_auto_session_name(self.input_file)


        # Waifu2x settings
        self.denoise_level = self.yaml["waifu2x"]["denoise_level"]
        self.tile_size = self.yaml["waifu2x"]["tile_size"]


        # Create default variables
        self.resolution = []
        self.valid_resolution = []
        self.fps = None
        self.frame_count = None
        self.frame_rate = None



        # Video related variables
        self.use_mediainfo = self.yaml["video"]["use_mediainfo"]


        # FFmpeg / FFprobe related
        self.get_frame_count_method = self.yaml["ffmpeg"]["get_frame_count_method"]
        self.get_frame_rate_method = self.yaml["ffmpeg"]["get_frame_rate_method"]
        self.get_resolution_method = self.yaml["ffmpeg"]["get_resolution_method"]


        # # Static developer vars across files

        # How much time in seconds to wait for waiting operations like until_exist()
        self.wait_time = self.yaml["developer"]["wait_time_exists"]


        # Resume options, TODO
        self.resume = False
        self.last_processing_frame = None


        ## Debug stuff

        # This might sound dumb but it's good to debug as waifu2x doens't upscale and mindisk remove stuff
        self.enable_waifu2x = self.yaml["debug"]["enable_waifu2x"]



        self.utils.log(color, debug_prefix, "Configuring context.* directories and static files")
    
        # Here we name the coresponding context.* directory var and set its "plain form"
        dirs = {
            "session": "sessions|SESSION",
            "residual": "sessions|SESSION|residual",
            "upscaled": "sessions|SESSION|upscaled",
            "iframes": "sessions|SESSION|iframes"
        }

        # If we happen to need some static files
        files = {
            "d2x_cpp_out": "sessions|SESSION|plugins_input.d2x",
            "context_vars": "sessions|SESSION|context_vars.yaml", # So Python / CPP can load these vars we set here on resume session
            "temp_vpy_script": "sessions|SESSION|temp_vpy_script.vpy"
        }

        # # # We declare these as none just for annoying errors on this dynamic variable setting

        self.session = self.residual = self.upscaled = self.iframes = self.d2x_cpp_out \
            = self.context_vars = self.temp_vpy_script = None

        # # #

        self.plain_dirs = []
        self.plain_files = []
        

        # This is a really neat way of micromanaging lots of self vars, we basically
        # set the self.$name$ with setattr, not much else is happening here other than
        # replacing SESSION with self.session_name and | with os.path.sep and
        # enumarating both dictionaries to save double the lines of code for dirs and files

        dir_and_file = [("dirs", dirs), ("files", files)]

        for _, reference in enumerate(dir_and_file):
            '''
            print(i, reference)

            0 ('dirs', {'residual': 'wor...
            1 ('files', {'d2x_cpp_out...

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

                self.utils.log(color, self.indentation, "(%s) self.%s = \"%s\"" % (printname, category, directory_or_file))



    # We save some selected vars for dandere2x_cpp to read them and work
    # properly based on where stuff actually is
    def save_vars(self):

        debug_prefix = "[Context.save_vars]"

        self.utils.log(color, debug_prefix, "Generating data dictionary")

        # # Build up the ata dictionary

        wanted = [
            "residual", "ROOT", "resume", "os", "input_file", "output_file",
            "block_size", "bleed", "session_name", "waifu2x_type", "resolution",
            "valid_resolution", "fps", "frame_count", "frame_rate", "session",
            "upscaled", "iframes", "d2x_cpp_out", "context_vars", "plain_dirs",
            "plain_files", "denoise_level", "tile_size", "last_processing_frame",
            "get_frame_count_method", "get_frame_rate_method"
        ]

        data = {}

        for item in wanted:

            # Get the self value of the item as variable name
            value = getattr(self, item)

            # In case the place the folder was changed
            if isinstance(value, str):
                value = value.replace(self.ROOT, self.rootfolder_substitution)

            if isinstance(value, list):
                try:
                    if isinstance(value[0], str):
                        value = [x.replace(self.ROOT, self.rootfolder_substitution) for x in value]
                except Exception as e:
                    self.utils.log(color_by_name("li_red"), debug_prefix, "Exception ocurred on line [%s]: " % self.utils.get_linenumber(), e)

            # Atribute
            data[item] = value
            


        self.utils.log(color, debug_prefix, "Saving vars dictionary to YAML file: [%s]" % self.context_vars)

        self.utils.save_yaml(data, self.context_vars)

        self.utils.log(color, debug_prefix, "Saved")

    
    # For resuming, loads into self.* variables the context_vars file
    def load_vars_from_file(self, context_vars_file):

        debug_prefix = "[Context.load_vars_from_file]"
        
        context_data = self.utils.load_yaml(context_vars_file)

        self.utils.log(color, debug_prefix, "Loaded context_vars yaml file, here's the self vars and loaded values:")

        for item in context_data:
            value = context_data[item]

            # As to revert back substituting <ROOTFOLDER>
            if isinstance(value, str):
                value = value.replace(self.rootfolder_substitution, self.ROOT)

            if isinstance(value, list):
                if isinstance(value[0], str):
                    value = [x.replace(self.rootfolder_substitution, self.ROOT) for x in value]

            # Log and set self var "self.item" as value
            self.utils.log(color, self.indentation, debug_prefix, "self.%s = \"%s\"" % (item, value))
            setattr(self, item, value)

