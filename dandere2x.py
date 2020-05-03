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

from d2xcpp import Dandere2xCPPWraper
from vp import VapourSynthWrapper
from controller import Controller
from processing import Processing
from d2xmath import D2XMath
from context import Context
from waifu2x import Waifu2x
from frame import Frame
from video import Video
from utils import Utils
from core import Core

import argparse
import time
import os


color = rgb(200, 255, 80)
phasescolor = rgb(84, 255, 87)
ROOT = os.path.dirname(os.path.abspath(__file__))


class Dandere2x():

    def __init__(self, args):
        self.args = args

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # NOTE DEBUG/DEVELOPMENT PURPOSES ONLY
        os.system("sh dandere2x_cpp_tremx/linux_compile_full.sh")

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
        self.controller = Controller(self.utils, self.context)

        # Let Utils access Controller
        self.utils.log(color, debug_prefix, "Giving Utils, Controller")
        self.utils.set_controller(self.controller)

        # Let Utils access Context
        self.utils.log(color, debug_prefix, "Giving Utils, Context")
        self.utils.set_context(self.context)

        # Deals with Video related stuff
        self.utils.log(color, debug_prefix, "Creating Video()")
        self.video = Video(self.context, self.utils, self.controller)

        # Our upscale wrapper, on which the default is Waifu2x
        self.utils.log(color, debug_prefix, "Creating Waifu2x()")
        self.waifu2x = Waifu2x(self.context, self.utils, self.controller)

        # Math utils, specific cases for Dandere2x
        self.utils.log(color, debug_prefix, "Creating D2XMath()")
        self.math = D2XMath(self.context, self.utils)

        # Dandere2x C++ wrapper
        self.utils.log(color, debug_prefix, "Creating Dandere2xCPPWraper()")
        self.d2xcpp = Dandere2xCPPWraper(self.context, self.utils, self.controller, self.video)

        # Deals with images, mostly numpy wrapper and special functions like block substitution
        self.utils.log(color, debug_prefix, "Creating Frame()")
        self.frame = Frame(self.context, self.utils, self.controller)

        # "Layers" of processing before the actual upscale from Waifu2x
        self.utils.log(color, debug_prefix, "Creating Processing()")
        self.processing = Processing(self.context, self.utils, self.controller, self.frame, self.video)

        # On where everything is controlled and starts
        self.utils.log(color, debug_prefix, "Creating Core()")
        self.core = Core(self.context, self.utils, self.controller, self.waifu2x, self.d2xcpp, self.processing)

        # Vapoursynth wrapper
        self.utils.log(color, debug_prefix, "Creating VapourSynthWrapper()")
        self.vapoursynth_wrapper = VapourSynthWrapper(self.context, self.utils, self.controller)




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


        # Warn the user and log mindisk mode
        if self.context.mindisk:
            self.utils.log(color, debug_prefix, "[MINDISK] [WARNING] MINDISK MODE [ON]")
        else:
            self.utils.log(color, debug_prefix, "[MINDISK] [WARNING] MINDISK MODE [OFF]")



        # NOT RESUME SESSION, delete previous session, load up and check directories
        if not self.context.resume:

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


            # Organization, if any filter applied just print a separator
            if any([self.context.apply_pre_noise, self.context.use_vapoursynth]):
                self.utils.log(phasescolor, "# # [Filter phase] # #")


            # If user chose to do so
            if self.context.apply_pre_noise:

                # Apply the noise
                self.video.apply_noise(self.context.input_file, self.context.noisy_video, "-vf noise=c1s=8:c0f=u")

                # As we applied and saved onto new file, that is our new input
                self.context.input_file = self.context.noisy_video

                exit()


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
                self.utils.log(color, debug_prefix, "Getting new video info [Vapoursynth can modify resolution]")
                self.video.get_video_info()

                self.utils.log(color, debug_prefix, "Showing new video info")
                self.video.show_info()


                # If we have already applied pre noise with ffmpeg, delete the old noisy file
                if self.context.apply_pre_noise:
                    if self.context.mindisk:
                        self.utils.log(color, debug_prefix, "[MINDISK] Deleting noisy video [%s]" % self.context.noisy_video)
                        self.utils.delete_file(self.context.noisy_video)
                    else:
                        self.utils.log(color, debug_prefix, "Mindisk mode OFF, DO NOT delete noisy video [%s]" % self.context.noisy_video)


            # Welp we don't need to add previous upscaled video if we're just starting
            self.video.ffmpeg.pipe_one_time(self.context.upscaled_video)


        # IS RESUME SESSION, basically load instructions from the context saved vars
        else:
            self.utils.log(color_by_name("li_red"), debug_prefix, "IS RESUME SESSION")

            self.utils.log(color, debug_prefix, "Loading Context vars from context_vars file")

            self.context.load_vars_from_file(self.context.context_vars)



    # Here's the core logic for Dandere2x, good luck other files
    def run(self):

        debug_prefix = "[Dandere2x.run]"

        self.d2xcpp.generate_run_command()


        if self.context.write_only_debug_video:
            self.utils.log(color, debug_prefix, "WRITE ONLY DEBUG VIDEO SET TO TRUE, CALLING CPP AND QUITTING")
            self.context.last_processing_frame = 0
            self.d2xcpp.run()
            self.controller.exit()
            return 0;


        # As now we get into the run part of Dandere2x, we don't really want to log
        # within the "global" log on the root folder so we move the logfile to session/log.log
        self.utils.move_log_file(self.context.logfile)



        self.video.frame_extractor.setup_video_input(self.context.input_file)

        self.video.frame_extractor.set_current_frame(self.context.last_processing_frame)

        # Test resume session
        # self.context.save_vars()
        # exit()


        # Simulate end of upscale
        #for i in range(2, 0, -1):
        #    self.utils.log(color, debug_prefix, i)
        #    time.sleep(1)



        #for thread in self.controller.threads:
        #    self.utils.log(color, debug_prefix, "Joining thread: [\"%s\"]" % thread)
        #    self.controller.threads[thread].join()





        '''
        self.video.ffmpeg.copy_videoA_audioB_to_other_videoC(
            "/home/tremeschin/github/clone/dandere2x-new/samples/demo.mkv",
            "/home/tremeschin/github/clone/dandere2x-new/samples/away.mkv",
            "/home/tremeschin/github/clone/dandere2x-new/samples/target.mkv"
        )
        '''


        self.utils.log(phasescolor, "# # [Run phase] # #")


        self.core.parse_whole_cpp_out()
        self.core.start()
        self.core.get_d2xcpp_vectors()





        # Simulate exiting
        self.utils.log(color, debug_prefix, "Simulating exit in 3 seconds")

        #for i in range(120, 0, -1):

        since_started = 0

        while True:
            if self.controller.stop:
                break
            if self.controller.upscale_finished:
                break
            self.utils.log(color, debug_prefix, "Time since started: %s" % since_started)
            since_started += 1
            time.sleep(1)

        if self.controller.upscale_finished:


            if self.context.use_vapoursynth:

                self.utils.log(color, debug_prefix, "APPLYING POST VAPOURSYNTH FILTER")

                if self.context.use_vapoursynth:
                    self.vapoursynth_wrapper.apply_filter(
                        self.context.vapoursynth_pos,
                        self.context.upscaled_video,
                        self.context.vapoursynth_processing
                    )

                    # Make the processed one the new upscaled
                    self.utils.delete_file(self.context.upscaled_video)
                    self.utils.rename(self.context.vapoursynth_processing, self.context.upscaled_video)


            # Migrate audio
            self.video.ffmpeg.copy_videoA_audioB_to_other_videoC(
                self.context.upscaled_video,
                self.context.input_file,
                self.context.joined_audio
            )

            # Delete old only upscaled video as migrated tracks
            self.utils.delete_file(self.context.upscaled_video)
            self.utils.rename(self.context.joined_audio, self.context.output_file)

            self.controller.exit()

            # Happy upscaled video :)

        else:
            self.context.save_vars()




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
