"""
===============================================================================

Purpose: Basic VapourSynth wrapper for applying filters on /vpys/ folder

Linux only for now TODO: Windows support

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


from git import Repo
from color import rgb, debug_color, color_by_name

import os


color = rgb(120, 230, 200)


class VapourSynthWrapper():
    def __init__(self, context, utils, controller):
        self.context = context
        self.utils = utils
        self.controller = controller

        if not self.context.use_vapoursynth:
            return None

        debug_prefix = "[VapourSynthWrapper.__init__]"

        # Windows users install packages with vsrepo
        if self.context.os == "windows" and False: # <++>

            # This is a repo name which is cloned in the externals folder
            vsrepo_path = self.context.ROOT + os.path.sep + "externals" + os.path.sep + "vsrepo"

            if not os.path.exists(vsrepo_path):

                self.utils.log(color, debug_prefix, "vsrepo not found in [\"%s\"], cloning it" % vsrepo_path)

                Repo.clone_from("https://github.com/vapoursynth/vsrepo", vsrepo_path)

                if os.path.exists(vsrepo_path):
                    self.utils.log(color, debug_prefix, "Cloned sucessfully!!")
                else:
                    self.utils.log(color, debug_prefix, "Error cloning git repo")
                    exit(-1)
            else:
                self.utils.log(color, debug_prefix, "Cloned vsrepo repo exists")
        else:
            self.utils.log(debug_color(), debug_prefix, "YOU'RE USING LINUX, SADLY WE CURRENTLY RELY YOU HAVE INSTALLED ALL THE VAPOURSYNTH PLUGINS YOU'RE GONNA USE")


        self.get_vspipe_bin()
        self.get_x264_bin()


    def get_vspipe_bin(self):

        debug_prefix = "[VapourSynthWrapper.get_vspipe_bin]"

        if self.context.os == "linux":
            self.utils.log(color, debug_prefix, "YOU'RE USING LINUX, MAKE SURE VSPIPE IS ACESSIBLE FROM A RAW SHELL (IN PATH)")
            self.vspipe_bin = "vspipe"
        else:
            self.utils.log(debug_color(), debug_prefix, "[ERROR] VAPOURSYNTH WINDOWS DOES NOT WORK YET")


    def get_x264_bin(self):

        debug_prefix = "[VapourSynthWrapper.get_vspipe_bin]"

        if self.context.os == "linux":
            self.utils.log(color, debug_prefix, "YOU'RE USING LINUX, MAKE SURE x264 IS ACESSIBLE FROM A RAW SHELL (IN PATH)")
            self.x264_bin = "x264"
        else:
            self.utils.log(debug_color(), debug_prefix, "[ERROR] VAPOURSYNTH WINDOWS DOES NOT WORK YET")


    def apply_filter(self, filter_name, input_video, output_video):

        debug_prefix = "[VapourSynthWrapper.apply_filter]"

        if not filter_name in ["null", "none"]:
            # Open
            with open(self.context.ROOT + os.path.sep + "vpys" + os.path.sep + filter_name + ".vpy", "r") as sc:
                with open(self.context.temp_vpy_script, "w") as temp:
                    temp.write(sc.read().replace("[INPUT]", input_video))

            # Couldn't get it working with subprocess...?
            # command = [self.vspipe_bin, "--y4m", self.context.temp_vpy_script, "-", "|", self.x264_bin, "--demuxer", "y4m", "-", "-o", output_video]

            command = "\"%s\" --y4m \"%s\" - | \"%s\" --demuxer y4m - -o \"%s\"" % \
                        (self.vspipe_bin, self.context.temp_vpy_script, self.x264_bin, output_video)

            if self.context.loglevel >= 3:
                self.utils.log(color, debug_prefix, "Command for vapoursynth filter processing is: [%s]" % command)

            self.utils.log(color_by_name("li_red"), debug_prefix, "[WARNING] MAY TAKE A WHILE DEPENDING ON CPU / VIDEO LENGHT / VIDEO RESOLUTION / VAPOURSYNTH STUFF USED")


            os.system(command)
