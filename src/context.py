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

from directories import Directories
from color import colors
import os


color = colors["context"]


class Context():

    def __init__(self, utils, config, failsafe):

        debug_prefix = "[Context.__init__]"

        # When logging isn't a simple line but something like a list or dictionary
        self.indentation = "··· | "

        # Set the (static) rootfolder substitution for changing paths session folders, so we can move the Dandere2x folder and be able to resume (?)
        self.rootfolder_substitution = "//ROOTFOLDER//"

        # Context needs Utils for logging and works based on a config
        self.utils = utils
        self.config = config
        
        # For absolute-reffering
        self.ROOT = self.utils.ROOT

        # Failsafe module
        self.failsafe = failsafe

        self.utils.log(color, 3, debug_prefix, "Rootfolder substitution is [%s] on Context and context_vars file" % self.rootfolder_substitution)

        if "resume_session_context_vars_file" in self.config:
            self.load_vars_from_file(self.config["resume_session_context_vars_file"])
            return

        # Session
        self.force = self.config["danger_zone"]["force"]

        # Get the operating system we're working with
        self.os = self.utils.get_os()
        self.utils.log(colors["warning"], 1, debug_prefix, "Got operating system: " + self.os)

        # Loglevel
        self.loglevel = self.config["developer"]["loglevel"]
        self.utils.log(colors["warning"], 1, debug_prefix, "LOGLEVEL: [%s]" % self.loglevel)

        # # Load variables

        # # # # See settings.yaml for a guide on the settings and what they are # # # #            

        # Video I/O
        self.input_file = self.config["basic"]["input_file"]
        self.output_file = self.config["basic"]["output_file"]

        # Session, "auto" is the input filename
        self.session_name = self.config["basic"]["session_name"]
        self.input_filename = self.utils.get_basename(self.input_file)

        # Windows uses ugly back slashes, failsafe
        if self.os == "windows":
            self.input_file = self.input_file.replace("/", "\\")

        # Block matching related
        self.block_size = self.config["block_matching"]["block_size"]
        self.bleed = self.config["block_matching"]["bleed"]
        self.dark_threshold = self.config["block_matching"]["dark_threshold"]
        self.bright_threshold = self.config["block_matching"]["bright_threshold"]
        self.upscale_full_frame_threshold = self.config["block_matching"]["upscale_full_frame_threshold"]

        # Upscaler settings
        self.upscaler_type = self.config["upscaler"]["type"]
        self.upscale_ratio = self.config["upscaler"]["upscale_ratio"]
        self.denoise_level = self.config["upscaler"]["denoise_level"]
        self.tile_size = self.config["upscaler"]["tile_size"]
        self.upscaler_model = self.config["upscaler"]["model"]
        self.load_proc_save = self.config["upscaler"]["load:proc:save"]
        self.w2x_converter_cpp_jobs = self.config["upscaler"]["w2x_converter_cpp_jobs"]
        self.linux_enable_mesa_aco_upscaler = self.config["upscaler"]["linux_enable_mesa_aco_upscaler"]

        # realsr-ncnn-vulkan must have upscale_ratio=4 as it's the only option
        if self.upscaler_type == "realsr-ncnn-vulkan":
            self.utils.log(color, 0, debug_prefix, "[WARNING] USING REALSR UPSCALER, FORCING UPSCALE_RATIO=4 FOR CONVENIENCE")
            self.upscale_ratio = 4

        # See if selected upscaler type and ratio / denoise are compatible
        self.failsafe.compatible_utype_uratio(self.upscaler_type, self.upscale_ratio)
        self.failsafe.compatible_upscaler_denoise(self.upscaler_type, self.denoise_level)

        # If the user did not sent us a absolute path
        self.input_file = os.path.abspath(self.input_file)

        # Output file can be auto, that is, append $UPSCALE_RATIO$x_$UPSCALER_TYPE$ at the start of the filename
        if self.output_file == "auto":
            # This is already absolute path as we just set input_file to one
            self.output_file = self.utils.auto_output_file(self.input_file, self.upscale_ratio, self.config["upscaler"]["type"])
            self.utils.log(color, 1, debug_prefix, "Output file set to \"auto\", assigning: [%s]" % self.output_file)
        else:
            # Else if it was manually set, get the absolute path for it
            self.output_file = os.path.abspath(self.output_file)
        
        # Get the new output filename if it was set to auto
        self.output_filename = self.utils.get_basename(self.output_file)

        # Check if input is file and output file directory exist, if not create it
        self.failsafe.check_input_output(self.input_file, self.output_file)

        # # The special case where the session name is "auto",
        # so we set it according to the input file "a.mkv" -> "a"
        if self.session_name == "auto":
            self.session_name = self.utils.get_auto_session_name(self.input_file)

        # Stats settings
        self.average_last_N_frames = self.config["stats"]["average_last_N_frames"]
        self.show_stats = self.config["stats"]["show_stats"]

        # Create default variables
        self.resolution = []
        self.valid_resolution = []
        self.frame_rate = None
        self.frame_count = None
        self.frame_rate = None
        self.resume = False
        self.last_processing_frame = 0
        self.zero_padding = 8  # We change this later on based on the frame_count
        self.total_upscale_time = 0

        # Video related variables
        self.get_video_info_method = self.config["video"]["get_video_info_method"]
        self.get_frame_count_method = self.config["video"]["get_frame_count_method"]
        self.get_frame_rate_method = self.config["video"]["get_frame_rate_method"]
        self.get_resolution_method = self.config["video"]["get_resolution_method"]

        # # FFmpeg / FFprobe related
        self.deblock_filter = self.config["ffmpeg"]["deblock_filter"]
        self.encode_codec = self.config["ffmpeg"]["encode_codec"]

        # x264 encoding
        self.x264_preset = self.config["ffmpeg"]["x264"]["preset"]
        self.x264_tune = self.config["ffmpeg"]["x264"]["tune"]
        self.x264_crf = self.config["ffmpeg"]["x264"]["crf"]

        # Dandere2x C++ specific
        self.mindisk = self.config["dandere2x_cpp"]["mindisk"]
        self.write_debug_video = int(self.config["dandere2x_cpp"]["write_debug_video"])
        self.show_debug_video_realtime = int(self.config["dandere2x_cpp"]["show_debug_video_realtime"])
        self.show_block_matching_stats = int(self.config["dandere2x_cpp"]["show_block_matching_stats"])
        self.only_run_dandere2x_cpp = int(self.config["dandere2x_cpp"]["only_run_dandere2x_cpp"])

        # # Developer variables

        # How much time in seconds to wait for waiting operations like until_exist()
        self.wait_time = self.config["developer"]["wait_time_exists"]
        self.upscaler_wait_for_residuals = self.config["developer"]["upscaler_wait_for_residuals"]

        # The range we'll delete the residuals
        self.safety_ruthless_residual_eliminator_range = self.config["developer"]["safety_ruthless_residual_eliminator_range"]

        # Will we be writing logs?
        self.write_log = self.config["developer"]["write_log"]

        # Vapoursynth settings
        self.use_vapoursynth = self.config["vapoursynth"]["enabled"]
        self.vapoursynth_pre = self.config["vapoursynth"]["pre"]
        self.vapoursynth_pos = self.config["vapoursynth"]["pos"]

        # This might sound dumb but it's good to debug as upscaler doesn't upscale and mindisk remove stuff
        self.enable_upscaler = self.config["debug"]["enable_upscaler"]

        # # # # Session directories / files # # # #
                
        self.utils.log(color, 4, debug_prefix, "Configuring context.* directories and static files")

        # Directories will handle for us a few tweaks we can do to the Dandere2x runtime
        self.directories = Directories()
        self.directories.input_filename = self.input_filename
        self.directories.session_name = self.session_name
        self.directories.generate_dirs()

        self.plain_dirs = self.directories.plain_dirs
        self.plain_files = self.directories.plain_files

        # We declare these as none just for annoying errors on this
        # dynamic variable setting workaround and for autocompleting

        self.residual = self.directories.get("residual")
        self.externals = self.directories.get("externals")
        self.upscaled = self.directories.get("upscaled")
        self.partial = self.directories.get("partial")
        self.processing = self.directories.get("processing")
        self.merged = self.directories.get("merged")
        self.session = self.directories.get("session")
        self.sessions_folder = self.directories.get("sessions_folder")

        self.upscaled_video = self.directories.get("upscaled_video")
        self.resume_video_frame = self.directories.get("resume_video_frame")
        self.debug_video = self.directories.get("debug_video")
        self.context_vars = self.directories.get("context_vars")
        self.temp_vpy_script = self.directories.get("temp_vpy_script")
        self.vapoursynth_processing = self.directories.get("vapoursynth_processing")
        self.joined_audio = self.directories.get("joined_audio")
        self.partial_video = self.directories.get("partial_video")
        self.logfile = self.directories.get("logfile")
        self.logfile_last_session = self.directories.get("logfile_last_session")

    # We save some selected vars for dandere2x_cpp to read them and work
    # properly based on where stuff actually is
    def save_vars(self):

        debug_prefix = "[Context.save_vars]"

        self.utils.log(color, 3, debug_prefix, "Generating data dictionary")

        # # Build up the data dictionary

        wanted = [
            "residual",
            "externals",
            "ROOT",
            "resume",
            "os",
            "input_file",
            "output_file",
            "block_size",
            "bleed",
            "session_name",
            "upscaler_type",
            "resolution",
            "valid_resolution",
            "frame_rate",
            "frame_count",
            "session",
            "upscaled",
            "merged",
            "context_vars",
            "plain_dirs",
            "plain_files",
            "denoise_level",
            "tile_size",
            "last_processing_frame",
            "get_frame_count_method",
            "get_frame_rate_method",
            "zero_padding",
            "loglevel",
            "input_filename",
            "output_filename",
            "load_proc_save",
            "mindisk",
            "use_vapoursynth",
            "vapoursynth_pre",
            "vapoursynth_pos",
            "frame_count",
            "get_video_info_method",
            "get_resolution_method",
            "wait_time",
            "upscaler_wait_for_residuals",
            "enable_upscaler",
            "vapoursynth_processing",
            "logfile",
            "temp_vpy_script",
            "upscaled_video",
            "upscale_ratio",
            "processing",
            "deblock_filter",
            "encode_codec",
            "safety_ruthless_residual_eliminator_range",
            "total_upscale_time",
            "dark_threshold",
            "bright_threshold",
            "sessions_folder",
            "logfile_last_session",
            "x264_preset",
            "x264_tune",
            "x264_crf",
            "write_log",
            "show_stats",
            "average_last_N_frames",
            "show_debug_video_realtime",
            "show_block_matching_stats",
            "write_debug_video",
            "only_run_dandere2x_cpp",
            "upscale_full_frame_threshold",
            "w2x_converter_cpp_jobs",
            "upscaler_model",
            "linux_enable_mesa_aco_upscaler",
            "force",
            "partial",
            "resume_video_frame",
            "joined_audio",
            "partial_video",
            "debug_video"
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
                    self.utils.log(colors["li_red"], 0, debug_prefix, "Exception ocurred on line [%s]: [%s]" % (self.utils.get_linenumber(), e))

            # Atribute
            data[item] = value
        
        self.utils.log(color, 5, debug_prefix, "Saving vars dictionary to YAML file: [%s]" % self.context_vars)

        self.utils.save_yaml(data, self.context_vars)
        
        self.utils.log(color, 5, debug_prefix, "Saved")

    # For resuming, loads into self.* variables the context_vars file
    def load_vars_from_file(self, context_vars_file):

        debug_prefix = "[Context.load_vars_from_file]"

        context_data = self.utils.load_yaml(context_vars_file)

        self.utils.log(color, 4, debug_prefix, "Loaded context_vars yaml file, here's the self vars and loaded values:")

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
            self.utils.log(color, 4, self.indentation + debug_prefix, "self.%s = \"%s\"" % (item, value))
            setattr(self, item, value)


if __name__ == "__main__":
    from utils import Miscellaneous
    Miscellaneous()
    print("You shouldn't be running this file directly, Dandere2x is class based and those are handled by dandere2x.py which is controlled by dandere2x_cli.py or a gui")
