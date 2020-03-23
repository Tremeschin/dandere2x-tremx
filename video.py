# pipe
# ffprobe vid info
# frame_compressor.py

from color import *

import os


color = rgb(30, 200, 60)


class Video():
    def __init__(self, context, utils):

        debug_prefix = "[Video.__init__]"

        self.context = context
        self.utils = utils

        self.ROOT = self.context.ROOT
        

    # Get video info with MediaInfo, don't process it yet
    def get_video_info(self):

        debug_prefix = "[Video.get_video_info]"

        self.input_file = self.context.input_file
        self.output_file = self.context.output_file 

        videofile = self.ROOT + os.path.sep + self.input_file

        self.utils.log(color, debug_prefix, "Video file is: [%s]" % videofile)


        # FFprobe looks like it have some issues on Linux so we're gonna use mediainfo
        # [TODO]: this looks like doesn't count the full frame count???
        # [TODO]: Windows will use .exe or use the old MediaInfo Python module?

        self.utils.log(color, debug_prefix, "Using mediainfo to get video info")
        
        # What output we want from mediainfo, and run it
        output_format = r'--Output="Video;%FrameCount%,%FrameRate%,%Width%,%Height%"'
        command = "mediainfo --fullscan %s \"%s\"" % (output_format, videofile)

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


        # # # Save them to Context

        self.context.resolution = self.resolution
        self.context.height = self.height 
        self.context.width = self.width
        
        self.context.frame_count = self.frame_count
        self.context.frame_rate = self.frame_rate
    

    # Self explanatory
    def show_info(self):
        
        debug_prefix = "[Video.show_info]"
        identation = "  >"

        self.utils.log(color, debug_prefix, "Here's the video info:")

        self.utils.log(color, identation, "Filename:", self.input_file)
        self.utils.log(color, identation, "Resolution: (%sx%s) // (WxH)" % (self.width, self.height))     
        self.utils.log(color, identation, "Frame count:", self.frame_count)
        self.utils.log(color, identation, "Frame rate:", self.frame_rate)

        