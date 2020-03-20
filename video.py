# pipe
# ffprobe vid info
# frame_compressor.py

from sty import fg, bg, ef, rs
from MediaInfo import MediaInfo

import os


color = fg.yellow


class Video():
    def __init__(self, context, utils):

        debug_prefix = "[Video.__init__]"

        self.context = context
        self.utils = utils

        self.ROOT = self.context.ROOT
        

    # Get video info with MediaInfo, don't process it yet
    def video_info(self):
        mi = MediaInfo(filename = self.ROOT + os.path.sep + self.input_file)
        self.info = mi.getInfo()


    # This we call video_info and set a few variables
    def configure_video_file(self):

        debug_prefix = "[Video.configure_video_file]"

        self.utils.log(color, debug_prefix, "Configuring video file..")

        self.input_file = self.context.input_file
        self.output_file = self.context.output_file

        # Get video info
        self.utils.log(color, debug_prefix, "Getting video info")
        self.video_info()

        self.utils.log(color, debug_prefix, "Atributing info got")
        
        # # Set variables

        # Resolution
        self.width = self.info["videoWidth"]
        self.height =self.info["videoHeight"]

        self.resolution = [self.width, self.height]

        # Frame count
        self.frame_count = self.info["videoFrameCount"]


        # # # Save them to Context

        self.context.resolution = self.resolution
        self.context.height = self.height 
        self.context.width = self.width
        
        self.context.frame_count = self.frame_count
    

    # Self explanatory
    def show_info(self):
        
        debug_prefix = "[Video.show_info]"
        identation = "  >"

        self.utils.log(color, debug_prefix, "Here's the video info:")

        self.utils.log(color, identation, "Filename:", self.input_file)
        self.utils.log(color, identation, "Resolution: (%sx%s) // (WxH)" % (self.width, self.height))     
        self.utils.log(color, identation, "Frame count:", self.frame_count)

        