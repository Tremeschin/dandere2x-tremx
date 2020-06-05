"""
===============================================================================

        Dandere2x - Fast upscaler Upscale!!

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

from d2xcpp import Dandere2xCPPWraper
from vp import VapourSynthWrapper
from controller import Controller
from processing import Processing
from d2xmath import Dandere2xMath
from stats import Dandere2xStats
from upscaler import Upscaler
from failsafe import FailSafe
from context import Context
from color import colors
from frame import Frame
from video import Video
from utils import Utils
from core import Core
import time
import sys
import os


color = colors["dandere2x"]
ROOT = os.path.dirname(os.path.abspath(__file__))


class Dandere2x():
    def __init__(self, config):
        self.config = config

        #os.system("sh dandere2x_cpp_tremx/linux_compile.sh")
        #os.system("sh dandere2x_cpp_tremx/linux_cross_compile_windows.sh")
        #exit()

    # This function loads up the "core" variables and objects
    def load(self):

        debug_prefix = "[Dandere2x.load]"
    
        # Create Utils
        self.utils = Utils()

        # Set the log file, here's why loglevel 0 isn't literally 0
        self.utils.clean_set_log()

        self.utils.log(colors["phases"], 3, debug_prefix, "# # [Load phase] # #")
        self.utils.log(color, 3, debug_prefix, "Created Utils()")

        # Check a few things and make sure the settings are compatible
        self.utils.log(color, 3, debug_prefix, "Creating FailSafe()")
        self.failsafe = FailSafe(self.utils)

        # Communication between files, static
        self.utils.log(color, 3, debug_prefix, "Creating Context()")
        self.context = Context(self.utils, self.config, self.failsafe)

        # Communication between files, depends on runtime
        self.utils.log(color, 3, debug_prefix, "Creating Controller()")
        self.controller = Controller(self.utils, self.context)

        # Let Utils access Controller
        self.utils.log(color, 3, debug_prefix, "Giving Utils, Controller")
        self.utils.set_controller(self.controller)

        # Let Utils access Context
        self.utils.log(color, 3, debug_prefix, "Giving Utils, Context")
        self.utils.set_context(self.context)

        # Stats
        self.utils.log(color, 3, debug_prefix, "Creating Dandere2xStats()")
        self.stats = Dandere2xStats(self.context, self.utils, self.controller)

        # Deals with Video related stuff
        self.utils.log(color, 3, debug_prefix, "Creating Video()")
        self.video = Video(self.context, self.utils, self.controller)

        # Deals with images, mostly numpy wrapper and special functions like block substitution
        self.utils.log(color, 3, debug_prefix, "Creating Frame()")
        self.frame = Frame

        # Our upscale wrapper, on which the default is upscaler
        self.utils.log(color, 3, debug_prefix, "Creating Upscaler()")
        self.upscaler = Upscaler(self.context, self.utils, self.controller, self.frame)

        # Math utils, specific cases for Dandere2x
        self.utils.log(color, 3, debug_prefix, "Creating Dandere2xMath()")
        self.d2xmath = Dandere2xMath(self.context, self.utils)

        # Dandere2x C++ wrapper
        self.utils.log(color, 3, debug_prefix, "Creating Dandere2xCPPWraper()")
        self.d2xcpp = Dandere2xCPPWraper(self.context, self.utils, self.controller, self.video, self.stats)

        # "Layers" of processing before the actual upscale from upscaler
        self.utils.log(color, 3, debug_prefix, "Creating Processing()")
        self.processing = Processing(self.context, self.utils, self.controller, self.frame, self.video, self.upscaler)

        # On where everything is controlled and starts
        self.utils.log(color, 3, debug_prefix, "Creating Core()")
        self.core = Core(self.context, self.utils, self.controller, self.upscaler, self.d2xcpp, self.processing, self.stats)

        # Vapoursynth wrapper
        self.utils.log(color, 3, debug_prefix, "Creating VapourSynthWrapper()")
        self.vapoursynth_wrapper = VapourSynthWrapper(self.context, self.utils, self.controller)

    # This function mainly configures things before upscaling and verifies stuff,
    # sees if it's a resume session, etc
    def setup(self):
        
        debug_prefix = "[Dandere2x.setup]"

        self.utils.log(colors["phases"], 3, debug_prefix, "# # [Setup phase] # #")

        # Make session folder
        self.utils.log(color, 3, debug_prefix, "Creating sessions directory if it doesn't exist [%s]" % self.context.sessions_folder)
        self.utils.mkdir_dne(self.context.sessions_folder)

        # Verify upscaler, get the binary
        self.utils.log(color, 3, debug_prefix, "Verifying upscaler")
        self.upscaler.verify()

        self.utils.log(color, 3, debug_prefix, "Generating run command from upscaler")
        self.upscaler.generate_run_command()

        # Warn the user and log mindisk mode
        if self.context.mindisk:
            self.utils.log(color, 2, debug_prefix, "[MINDISK] [WARNING] MINDISK MODE [ON]")
        else:
            self.utils.log(color, 2, debug_prefix, "[MINDISK] [WARNING] MINDISK MODE [OFF]")

        # Check if context_vars file exist and is set to be resume
        # If force argument is set, force not resume session
        if self.context.force:
            self.utils.log(colors["hard_warning"], 0, debug_prefix, "FORCE MODE ENABLED, FORCING RESUME=FALSE")
            # Set resume and force to false as both aren't true anymore
            self.context.resume = False
            self.context.force = False
        else:
            self.utils.log(color, 1, debug_prefix, "Checking if is Resume session")
            self.context.resume = self.utils.check_resume()

        # NOT RESUME SESSION, delete previous session, load up and check directories
        if not self.context.resume:

            # Log and reset session directory
            self.utils.log(colors["li_red"], 0, debug_prefix, "NOT RESUME SESSION, deleting session [%s]" % self.context.session_name)
            self.utils.rmdir(self.context.session)

            # Check dirs
            self.utils.log(color, 3, debug_prefix, "Checking directories")
            self.utils.check_dirs()

            # Reset files
            self.utils.log(color, 3, debug_prefix, "Reseting files")
            self.utils.reset_files()

            # Debugging, show static files
            self.utils.log(color, 3, debug_prefix, "Showing static files")
            self.utils.show_static_files()

            # Get video info
            self.utils.log(color, 3, debug_prefix, "Getting video info")
            self.video.get_video_info()
            self.utils.log(color, 3, debug_prefix, "Showing video info")
            self.video.show_info()

            # Values that should be setted up automatically
            self.d2xmath.set_block_size()

            # Save vars of context so we can resume it later
            self.utils.log(color, 3, debug_prefix, "Saving Context vars to file")
            self.context.save_vars()

            # Apply pre vapoursynth filter
            if self.context.use_vapoursynth:

                # Apply pre filter
                self.vapoursynth_wrapper.apply_filter(
                    self.context.vapoursynth_pre,
                    self.context.input_file,
                    self.context.vapoursynth_processing
                )

                # As we applied pre filter, our input video is now the processed one by vapoursynth
                self.context.input_file = self.context.vapoursynth_processing

                # # As something like a transpose can modify the video resolution we get the new info

                # Get video info
                self.utils.log(color, 3, debug_prefix, "Getting new video info [Vapoursynth can modify resolution]")
                self.video.get_video_info()

                self.utils.log(color, 3, debug_prefix, "Showing new video info")
                self.video.show_info()

        # IS RESUME SESSION, basically load instructions from the context saved vars
        else:
            self.utils.log(colors["li_red"], debug_prefix, 0, "IS RESUME SESSION")

            # Delete previous residuals / upscaled as they can cause some trouble
            self.utils.log(color, 1, debug_prefix, "[FAILSAFE] DELETING RESIDUAL, UPSCALE DIR AND PLUGINS INPUT FILE")
            self.utils.rmdir(self.context.residual)
            self.utils.rmdir(self.context.upscaled)

            # We just deleted two dirs, so gotta make sure they exist
            self.utils.log(color, 1, debug_prefix, "[FAILSAFE] REGENERATING DIRS")
            self.utils.check_dirs()

            # Load previous stopped session from the context
            self.utils.log(color, 1, debug_prefix, "Loading Context vars from context_vars file")
            self.context.load_vars_from_file(self.context.context_vars)

            # Get the last frame we piped to the last partial video as the starting frame of the next partial
            self.video.save_last_frame_of_video_ffmpeg(self.utils.get_last_partial_video_path(), self.context.resume_video_frame)
        
        # Create the encoding FFmpeg pipe
        self.video.ffmpeg.pipe_one_time(self.utils.get_partial_video_path())

    # Here's the core logic for Dandere2x
    def run(self):

        debug_prefix = "[Dandere2x.run]"

        # Generate the command to run Dandere2x C++
        self.d2xcpp.generate_run_command()

        # Only run Dandere2x C++
        if self.context.only_run_dandere2x_cpp:
            self.context.mindisk = False
            self.d2xcpp.generate_run_command()
            self.utils.log(color, 0, debug_prefix, "WRITE ONLY DEBUG VIDEO SET TO TRUE, CALLING CPP AND QUITTING")
            self.context.last_processing_frame = 0
            self.d2xcpp.run()
            self.controller.exit()
            return 0

        # As now we get into the run part of Dandere2x, we don't really want to log
        # within the "global" log on the root folder so we move the logfile to session/log.log
        self.utils.move_log_file(self.context.logfile)

        self.utils.log(colors["phases"], 3, debug_prefix, "# # [Run phase] # #")

        # Start core Dandere2x, ie, start the threads
        self.core.start()

        # Set resume to True as we just started Dandere2x
        # It's not a good idea to stop an session early on, can yield blank videos and will not be merged properly at the end
        self.context.resume = True

        # Show the user we're still alive
        while True:

            # If controller stops or upscale is finished, break
            if self.controller.stop:
                break
            if self.controller.upscale_finished:
                break
            if not self.context.show_stats:
                self.utils.log(color, 1, debug_prefix, "Total upscale time: %s" % self.context.total_upscale_time)

            self.context.total_upscale_time += 1
            time.sleep(1)

        # # When we exit the while loop before either we finished or we stopped

        # If we finished
        if self.controller.upscale_finished:

            # How many partials videos there is on the session partial directory?
            partials = len(os.listdir(self.context.partial))

            # 1? Just copy it to the upscaled video
            if partials == 1:
                self.utils.rename(self.context.partial + "0.mkv", self.context.upscaled_video)

            # More than 1? Concatenate all of them
            elif partials > 1:
                # If we have two or more partials video
                self.video.ffmpeg.concat_video_folder_reencode(self.context.partial, self.context.upscaled_video)

                # Delete the partial dir
                self.utils.rmdir(self.context.partial)

            # None? oops, error
            else:
                self.utils.log(color, 0, debug_prefix, "[ERROR] No partials were found in [%s]" % self.context.partial)
                sys.exit(-1)

            # We still gotta add the audio to the upscaled file or / and post filters we might be interested into

            # Apply post vapoursynth filter as the upscale finished
            if self.context.use_vapoursynth:

                self.utils.log(color, 1, debug_prefix, "APPLYING POST VAPOURSYNTH FILTER")

                if self.context.use_vapoursynth:
                    self.vapoursynth_wrapper.apply_filter(
                        self.context.vapoursynth_pos,
                        self.context.upscaled_video,
                        self.context.vapoursynth_processing
                    )

                    # Make the processed one the new upscaled
                    self.utils.delete_file(self.context.upscaled_video)
                    self.utils.rename(self.context.vapoursynth_processing, self.context.upscaled_video)

            # Migrate audio tracks from the original video to the new one
            self.video.ffmpeg.copy_videoA_audioB_to_other_videoC(
                self.context.upscaled_video,
                self.context.input_file,
                self.context.joined_audio
            )

            # Delete old only upscaled video as migrated tracks
            self.utils.delete_file(self.context.upscaled_video)
            self.utils.rename(self.context.joined_audio, self.context.output_file)

            self.utils.log(color, 1, debug_prefix, "Total upscale time: %s" % self.context.total_upscale_time)
            
            # Move the logfile to the root folder as we're gonna delete the session folder
            self.utils.log(color, 1, debug_prefix, "Moving session log to root Dandere2x folder and Removing session folder [%s]" % self.context.session)
            self.utils.rename(self.context.logfile, self.context.logfile_last_session)

            # For removing the dir we gotta have a writable log file
            self.utils.logfile = self.context.logfile_last_session

            # Remove session folder as we finished everything
            self.utils.rmdir(self.context.session)
            
            # Happy upscaled video :)

        else:
            # Save progress for later resuming
            self.context.save_vars()

            self.utils.log(color, 0, debug_prefix, "Exiting Dandere2x.run")


if __name__ == "__main__":
    print("You shouldn't be running this file directly, Dandere2x is class based and those are handled by dandere2x.py which is controlled by dandere2x_cli.py or a gui")
