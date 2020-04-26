"""
===============================================================================

Purpose: Deals with Video related stuff, also a FFmpeg wrapper in its own class

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


# pipe
# ffprobe vid info
# frame_compressor.py

from color import rgb, color_by_name

import subprocess
import threading
import os


color = rgb(30, 200, 60)


class FFmpegWrapper():
    def __init__(self, context, utils, controller):

        debug_prefix = "[Video.FFmpegWrapper]"

        self.context = context
        self.utils = utils
        self.controller = controller

        self.ffmpeg_binary = self.utils.get_binary("ffmpeg")
        self.ffprobe_binary = self.utils.get_binary("ffprobe")

        self.utils.log(color, debug_prefix, "Init")




    # # # # # # # # # # # # # SESSION DEDICATED TO GETTING VIDEO INFO # # # # # # # # # # # # #


    def get_frame_count_with_null_copy(self, video_file):
        
        # ffmpeg -i input.mkv -map 0:v:0 -c copy -f null -

        debug_prefix = "[Video.get_frame_count_with_null_copy]"

        self.utils.log(color, debug_prefix, "[WARNING] CHECKING VIDEO FRAME COUNT SAFE WAY, MAY TAKE A WHILE DEPENDING ON CPU AND VIDEO LENGTH")


        # Build the command to get the frame_count with "null copy" mode
        command = ["%s" % self.ffmpeg_binary, "-i", "%s" % video_file, "-map", "0:v:0", "-c", "copy", "-f", "null", "-"]

        self.utils.log(color, debug_prefix, "Command to check frame_count is: [%s]" % ' '.join(command))


        # We have to use subprocess here as os.popen doesn't catch the output correctly
        info = self.utils.command_output_subprocess(command)
        frame_count = None


        if self.context.loglevel >= 6:
            self.utils.log(color, debug_prefix, "[DEBUG] COMMAND OUTPUT:")
            self.utils.log(rgb(255,255,255), debug_prefix, info)


        # Iterate through the output lines
        for line in info.split("\n"):
            if "frame=" in line:

                if self.context.loglevel >= 2:
                    self.utils.log(color, debug_prefix, "Line with \"frames=\" in it: [%s]" % line)

                # Transform every non single whitespace to one single whitespace
                line = ' '.join(line.split())

                frame_count = self.utils.get_nth_word(line, 2)
                frame_count = int(frame_count)

                self.utils.log(color, debug_prefix, "Got frame count: [%s]" % frame_count)
        
        # Fail safe
        if frame_count == None:
            self.utils.log(color_by_name("li_red"), debug_prefix, "[ERROR] COULDN'T GET FRAME COUNT")
            self.controller.exit()

        return frame_count
    



    def get_resolution_with_ffprobe(self, video_file):

        # ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of default=nw=1 input.mp4

        debug_prefix = "[Video.get_resolution_with_ffprobe]"
        
        wanted = {
            "width": None,
            "height": None
        }

        command = [self.ffprobe_binary, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "default=nw=1", video_file]

        self.utils.log(color, debug_prefix, "Command to check resolution is: [%s]" % ' '.join(command))


        # We have to use subprocess here as os.popen doesn't catch the output correctly
        info = self.utils.command_output_subprocess(command)

        if self.context.loglevel >= 6:
            self.utils.log(color, debug_prefix, "[DEBUG] COMMAND OUTPUT:")
            self.utils.log(rgb(255,255,255), debug_prefix, info)


        # Iterate in the output lines
        for line in info.split("\n"):

            line = line.replace("\n", "")

            # Parse the line

            if "width" in line:
                if self.context.loglevel >= 3:
                    self.utils.log(color, debug_prefix, "Line with width: [%s]" % line)

                wanted["width"] = int(line.split("=")[1])
                

            if "height" in line:
                if self.context.loglevel >= 3:
                    self.utils.log(color, debug_prefix, "Line with height: [%s]" % line)

                wanted["height"] = int(line.split("=")[1])

        self.utils.log(color, debug_prefix, "Got width: [%s] and height: [%s]" % (wanted["width"], wanted["height"]))

        return wanted


    

    def get_frame_rate_with_ffprobe(self, video_file):

        # ffprobe -v 0 -of csv=p=0 -select_streams v:0 -show_entries stream=r_frame_rate infile

        debug_prefix = "[Video.get_resolution_with_ffprobe]"

        command = [self.ffprobe_binary, "-v", "0", "-of", "csv=p=0", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", video_file]


        self.utils.log(color, debug_prefix, "Command to check frame_rate is: [%s]" % ' '.join(command))


        # We have to use subprocess here as os.popen doesn't catch the output correctly
        frame_rate = self.utils.command_output_subprocess(command).replace("\n", "")

        self.utils.log(color, debug_prefix, "Got frame rate output: [%s]" % frame_rate)
        

        # NOTE: this returns the "division" as in 2997/100 fps, or 30/1

        return frame_rate




    def get_video_info(self, video_file):

        debug_prefix = "[Video.get_video_info]"

        video_info = {
            "frame_count": None,
            "frame_rate": None,
            "width": None,
            "height": None,
        }


        # # Get the frame count


        # Get the frame count
        if self.context.get_frame_count_method == "null_copy":
            self.utils.log(color, debug_prefix, "[INFO] Getting video [frame_count] info with [NULL COPY] method")
            video_info["frame_count"] = self.get_frame_count_with_null_copy(video_file)

        

        # Get the resolution
        if self.context.get_resolution_method == "ffprobe":
            self.utils.log(color, debug_prefix, "[INFO] Getting video [resolution] info with [ffprobe] method")
            resolution = self.get_resolution_with_ffprobe(video_file)
            video_info["width"] = resolution["width"]
            video_info["height"] = resolution["height"]

            

        # Get the frame rate
        if self.context.get_frame_rate_method == "ffprobe":
            self.utils.log(color, debug_prefix, "[INFO] Getting video [frame_rate] info with [ffprobe] method")
            video_info["frame_rate"] = self.get_frame_rate_with_ffprobe(video_file)


        self.frame_count = video_info["frame_count"]
        self.frame_rate = video_info["frame_rate"]

        # Resolution
        self.width = video_info["width"]
        self.height = video_info["height"]

        return video_info


    # # # # # # # # # # # # END SESSION DEDICATED TO GETTING VIDEO INFO # # # # # # # # # # # #










class Video():
    def __init__(self, context, utils, controller):

        debug_prefix = "[Video.__init__]"

        self.context = context
        self.utils = utils
        self.controller = controller

        self.ROOT = self.context.ROOT

        self.ffmpeg = FFmpegWrapper(self.context, self.utils, self.controller)

        self.utils.log(color, debug_prefix, "Init")
    


    def get_video_info_with_mediainfo(self, video_path):

        debug_prefix = "[Video.get_video_info_with_mediainfo]"

        self.utils.log(color, debug_prefix, "Using mediainfo to get video info")
        
        # What output we want from mediainfo, and run it
        output_format = r'--Output="Video;%FrameCount%,%FrameRate%,%Width%,%Height%"'
        command = "%s --fullscan %s \"%s\"" % (self.utils.get_binary("mediainfo"), output_format, video_path)

        self.utils.log(color, debug_prefix, "Command to get info is: [%s]" % command)

        out = self.utils.command_output(command).replace("\n", "")

        self.utils.log(color, debug_prefix, "Got output: [%s]" % out)
        
        # Remove the new line and split by commas
        out = out.split(",")


        # # Set variables
        self.utils.log(color, debug_prefix, "Got info, setting vars")

        # Frame 
        self.frame_count = int(out[0])
        self.frame_rate = float(out[1])

        # Resolution
        self.width = int(out[2])
        self.height = int(out[3])

        self.resolution = [self.width, self.height]





    # Get video information with FFprobe
    def get_video_info_with_ffmpeg(self, video_path):

        #debug_prefix = "[Video.get_video_info_with_ffprobe]"

        video_info = self.ffmpeg.get_video_info(video_path)

        # Frame 
        self.frame_count = video_info["frame_count"]
        self.frame_rate = video_info["frame_rate"]

        # Resolution
        self.width = video_info["width"]
        self.height = video_info["height"]





    # Get video info with MediaInfo, don't process it yet
    def get_video_info(self):

        debug_prefix = "[Video.get_video_info]"

        self.input_file = self.context.input_file
        self.output_file = self.context.output_file 

        video_path = self.ROOT + os.path.sep + self.input_file

        self.utils.log(color, debug_prefix, "Video file is: [%s]" % video_path)


        # Get the video info

        if self.context.use_mediainfo:
            self.get_video_info_with_mediainfo(video_path)
        else:
            self.get_video_info_with_ffmpeg(video_path)


        # # Save info to context

        self.resolution = [self.width, self.height]

        self.context.resolution = self.resolution
        self.context.height = self.height 
        self.context.width = self.width
        
        self.context.frame_count = self.frame_count
        self.context.frame_rate = self.frame_rate




    # Self explanatory
    def show_info(self):
        
        debug_prefix = "[Video.show_info]"

        self.utils.log(color, debug_prefix, "Here's the video info:")

        self.utils.log(color, self.context.indentation, "Filename: [%s]" % self.input_file)
        self.utils.log(color, self.context.indentation, "Resolution: (%sx%s)" % (self.width, self.height))     
        self.utils.log(color, self.context.indentation, "Frame count: [%s]" % self.frame_count)
        self.utils.log(color, self.context.indentation, "Frame rate: [%s]" % self.frame_rate)

        