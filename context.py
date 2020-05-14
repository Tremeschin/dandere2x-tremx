"""
===============================================================================

Purpose: Class Context() deals with multiple file communications and mostly
"static" variables, or "global constants", as in "session settings"

Yes that is very dangerous and not recommended however this works really really
good as basically this class is accessible on almost all Dandere2x Python files
files and it's used as a reference on the current state of the program. Also we
save this variables here and load them up when resuming sessions, so it's
a way of making persistent session based variables without much trouble

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

from color import color_by_name, fg

import os


color = color_by_name("li_yellow")


class Context():

    def __init__(self, utils):
        self.indentation = "··· |"
        debug_prefix = "[Context.__init__]"

        self.utils = utils

        # Set the (static) rootfolder substitution for changing paths session folders
        self.rootfolder_substitution = "//ROOTFOLDER//"
        self.utils.log(color, debug_prefix, "Rootfolder substitution is [%s] on Context and context_vars file" % self.rootfolder_substitution)

        # For absolute-reffering
        self.ROOT = self.utils.ROOT
        self.os = self.utils.get_os()

        self.utils.log(fg.li_red, debug_prefix, "Got operating system: " + self.os)

        # Load up the yaml file
        self.utils.log(color, debug_prefix, "Loading settings YAML file")

        self.yaml = self.utils.load_yaml(self.ROOT + os.path.sep + "settings.yaml")

        # Loglevel
        self.loglevel = self.yaml["developer"]["loglevel"]

        self.utils.log(fg.li_red, debug_prefix, "LOGLEVEL: [%s]" % self.loglevel)

        # Create context dict
        self.utils.log(color, debug_prefix, "Creating Context dictionary")

        self.context = {}
        self.context["ROOT"] = self.utils.ROOT

        # # # Static Variables # # #
        self.utils.log(color, debug_prefix, "Setting up static variables")

        # Load basic variables

        # # Video I/O

        self.input_file = self.yaml["basic"]["input_file"]
        self.output_file = self.yaml["basic"]["output_file"]

        # If the user did not sent us a absolute path
        if not os.path.isabs(self.input_file):
            self.input_file = self.ROOT + os.path.sep + self.input_file

        if not os.path.isabs(self.output_file):
            self.output_file = self.ROOT + os.path.sep + self.output_file

        self.input_filename = self.utils.get_basename(self.input_file)
        self.output_filename = self.utils.get_basename(self.output_file)

        # #

        # Load processing variables
        self.extracted_images_extension = self.yaml["processing"]["extracted_images_extension"]
        self.block_size = self.yaml["processing"]["block_size"]
        self.bleed = self.yaml["processing"]["bleed"]

        # "Global" or non-indented options as they're "major"
        self.session_name = self.yaml["session_name"]
        self.waifu2x_type = self.yaml["waifu2x_type"]
        self.mindisk = self.yaml["mindisk"]

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
        print(self.yaml["waifu2x"])
        self.linux_enable_mesa_aco_waifu2x_vulkan = self.yaml["waifu2x"]["linux_enable_mesa_aco_waifu2x_vulkan"]

        # Create default variables
        self.resolution = []
        self.valid_resolution = []
        self.frame_rate = None
        self.frame_count = None
        self.frame_rate = None

        # Video related variables
        self.get_video_info_method = self.yaml["video"]["get_video_info_method"]
        self.get_frame_count_method = self.yaml["video"]["get_frame_count_method"]
        self.get_frame_rate_method = self.yaml["video"]["get_frame_rate_method"]
        self.get_resolution_method = self.yaml["video"]["get_resolution_method"]

        # FFmpeg / FFprobe related
        self.deblock_filter = self.yaml["ffmpeg"]["deblock_filter"]
        self.encode_codec = self.yaml["ffmpeg"]["encode_codec"]

        # # Static developer vars across files

        # How much time in seconds to wait for waiting operations like until_exist()
        self.wait_time = self.yaml["developer"]["wait_time_exists"]
        self.waifu2x_wait_for_residuals = self.yaml["developer"]["waifu2x_wait_for_residuals"]
        self.safety_ruthless_residual_eliminator_range = self.yaml["developer"]["safety_ruthless_residual_eliminator_range"]

        # # # Literal constants

        # Default zero padding level for saving files,
        # we change it based on the frame count as it fullfils our necessity
        self.zero_padding = 8

        # # # # # # # # # # # # # # # # # # # #

        # Resume options, TODO
        self.resume = False
        self.last_processing_frame = 0

        # # Debug stuff

        # This might sound dumb but it's good to debug as waifu2x doens't upscale and mindisk remove stuff
        self.enable_waifu2x = self.yaml["debug"]["enable_waifu2x"]
        self.write_only_debug_video = self.yaml["debug"]["write_only_debug_video"]

        self.utils.log(color, debug_prefix, "Configuring context.* directories and static files")

        # Here we name the coresponding context.* directory var and set its "plain form"
        dirs = {
            "residual": "//ROOT//|sessions|//SESSION//|residual|",
            "upscaled": "//ROOT//|sessions|//SESSION//|upscaled|",
            "partial": "//ROOT//|sessions|//SESSION//|partial|",
            "merged": "//ROOT//|sessions|//SESSION//|merged|",
            "processing": "//ROOT//|sessions|//SESSION//|processing",
            "session": "//ROOT//|sessions|//SESSION//"
        }

        # "Static" files location
        files = {
            "d2x_cpp_plugins_out": "//ROOT//|sessions|//SESSION//|plugins_input.d2x",
            "d2x_cpp_vectors_out": "//ROOT//|sessions|//SESSION//|vectors.d2x",
            "upscaled_video": "//ROOT//|sessions|//SESSION//|upscaled_//INPUTVIDEOFILENAME//",
            "partial_video": "//ROOT//|sessions|//SESSION//|partial|//NUM//.mkv",  # We make an exception on this in Utils.reset_files
            "resume_video_frame": "//ROOT//|sessions|//SESSION//|processing|resume_video_frame.jpg",  # We make an exception on this in Utils.reset_files
            "debug_video": "//ROOT//|sessions|//SESSION//|debug_video.mkv",
            "context_vars": "//ROOT//|sessions|//SESSION//|context_vars.yaml",
            "temp_vpy_script": "//ROOT//|sessions|//SESSION//|temp_vpy_script.vpy",
            "original_audio_file": "//ROOT//|sessions|//SESSION//|processing|original_audio.aac", # Deprecated?
            "noisy_video": "//ROOT//|sessions|//SESSION//|processing|noisy_//INPUTVIDEOFILENAME//",
            "vapoursynth_processing": "//ROOT//|sessions|//SESSION//|processing|vapoursynth_//INPUTVIDEOFILENAME//",
            "joined_audio": "//ROOT//|sessions|//SESSION//|processing|joined_audio_//INPUTVIDEOFILENAME//",
            "logfile": "//ROOT//|sessions|//SESSION//|log.log"
        }

        # # # We declare these as none just for annoying errors on this
        # dynamic variable setting workaround and for autocompleting

        self.residual = None
        self.upscaled = None
        self.partial = None
        self.merged = None
        self.session = None

        self.d2x_cpp_vectors_out = None
        self.d2x_cpp_plugins_out = None
        self.upscaled_video = None
        self.resume_video_frame = None
        self.debug_video = None
        self.context_vars = None
        self.temp_vpy_script = None
        self.noisy_video = None
        self.vapoursynth_processing = None
        self.joined_audio = None
        self.logfile = None

        # # #

        self.plain_dirs = []
        self.plain_files = []

        # This is a really neat* way of micromanaging lots of self vars, we basically
        # set the self.$name$ with setattr, not much else is happening here other than
        # replacing SESSION with self.session_name and | with os.path.sep and
        # enumarating both dictionaries to save double the lines of code for dirs and files
        # *and weird?

        dir_and_file = [("dirs", dirs), ("files", files)]

        for _, reference in enumerate(dir_and_file):
            '''
            print(i, reference)

            0 ('dirs', {'residual': 'wor...
            1 ('files', {'d2x_cpp_plugins_out...

            This way we can have the reference[0] which is the name and reference[1]
            which is the full dictionary
            '''

            name = reference[0]
            dic = reference[1]

            for category in dic:

                # # # Getting the full directory and add it to plain_{dirs,files} list # # #

                # Replace our syntax with system-specific one, you'll know
                # seeing the dictionary in the next line:

                # We use //NAME// because either on Windows or Linux dirs can't have this name
                # so instead of using a nullbyte or something else for replacing the "dynamic stuff"
                # se simply use this workaround, note the "|" = os.path.sep MUST BE THE LAST
                replace = {
                    "//SESSION//": self.session_name,
                    "//INPUTVIDEOFILENAME//": self.input_filename,
                    "//ROOT//": self.ROOT,

                    "|": os.path.sep,  # THIS MUST BE THE LAST
                }

                # The "path" itself, with the "|" and "SESSION"
                subname = dic[category]

                for item in replace:
                    subname = subname.replace(item, replace[item])

                # # Pretty logging

                if name == "dirs":
                    self.plain_dirs.append(subname)
                    printname = "directory"

                elif name == "files":
                    self.plain_files.append(subname)
                    printname = "static files"

                # #

                # Set the value based on the "category" -> self.residual, self.upscaled, self.merged
                setattr(self, category, subname)

                self.utils.log(color, self.indentation, "(%s) self.%s = \"%s\"" % (printname, category, subname))

    # We save some selected vars for dandere2x_cpp to read them and work
    # properly based on where stuff actually is
    def save_vars(self):

        debug_prefix = "[Context.save_vars]"

        self.utils.log(color, debug_prefix, "Generating data dictionary")

        # # Build up the ata dictionary

        wanted = [
            "residual", "ROOT", "resume", "os", "input_file", "output_file",
            "block_size", "bleed", "session_name", "waifu2x_type", "resolution",
            "valid_resolution", "frame_rate", "frame_count", "session",
            "upscaled", "merged", "d2x_cpp_plugins_out", "context_vars", "plain_dirs",
            "plain_files", "denoise_level", "tile_size", "last_processing_frame",
            "get_frame_count_method", "get_frame_rate_method", "zero_padding",
            "loglevel", "input_filename", "output_filename", "extracted_images_extension",
            "mindisk", "use_vapoursynth", "vapoursynth_pre", "vapoursynth_pos", "frame_count",
            "get_video_info_method", "get_resolution_method", "wait_time",
            "waifu2x_wait_for_residuals", "enable_waifu2x", "vapoursynth_processing",
            "logfile", "temp_vpy_script", "original_audio_file", "upscaled_video",
            "processing", "d2x_cpp_vectors_out", "deblock_filter", "encode_codec",
            "safety_ruthless_residual_eliminator_range"
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
                    if value == []:
                        pass
                    elif isinstance(value[0], str):
                        value = [x.replace(self.ROOT, self.rootfolder_substitution) for x in value]
                except Exception as e:
                    self.utils.log(color_by_name("li_red"), debug_prefix, "Exception ocurred on line [%s]: [%s]" % (self.utils.get_linenumber(), e))

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
                if value == []:
                    pass
                elif isinstance(value[0], str):
                    value = [x.replace(self.rootfolder_substitution, self.ROOT) for x in value]

            # Log and set self var "self.item" as value
            self.utils.log(color, self.indentation, debug_prefix, "self.%s = \"%s\"" % (item, value))
            setattr(self, item, value)
