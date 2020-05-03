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
import cv2
import os


color = rgb(30, 200, 60)


class FFmpegWrapper():
    def __init__(self, context, utils, controller):

        debug_prefix = "[FFmpegWrapper.__init__]"

        self.context = context
        self.utils = utils
        self.controller = controller

        self.ffmpeg_binary = self.utils.get_binary("ffmpeg")
        self.ffprobe_binary = self.utils.get_binary("ffprobe")

        self.utils.log(color, debug_prefix, "Init")




    # # # # # # # # # # # # # SESSION DEDICATED TO GETTING VIDEO INFO # # # # # # # # # # # # #


    def get_frame_count_with_null_copy(self, video_file):

        # ffmpeg -i input.mkv -map 0:v:0 -c copy -f null -

        debug_prefix = "[FFmpegWrapper.get_frame_count_with_null_copy]"

        self.utils.log(color, debug_prefix, "[WARNING] CHECKING VIDEO FRAME COUNT SAFE WAY, MAY TAKE A WHILE DEPENDING ON CPU AND VIDEO LENGTH")


        # Build the command to get the frame_count with "null copy" mode
        command = ["%s" % self.ffmpeg_binary, "-loglevel", "warning", "-stats", "-i", "%s" % video_file, "-map", "0:v:0", "-c", "copy", "-f", "null", "-"]

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

                frame_count = line.split("fps")[0].split("=")[1]
                frame_count = int(frame_count)

                self.utils.log(color, debug_prefix, "Got frame count: [%s]" % frame_count)

        # Fail safe
        if frame_count == None:
            self.utils.log(color_by_name("li_red"), debug_prefix, "[ERROR] COULDN'T GET FRAME COUNT")
            self.controller.exit()

        return frame_count




    def get_resolution_with_ffprobe(self, video_file):

        # ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of default=nw=1 input.mp4

        debug_prefix = "[FFmpegWrapper.get_resolution_with_ffprobe]"

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

        debug_prefix = "[FFmpegWrapper.get_resolution_with_ffprobe]"

        command = [self.ffprobe_binary, "-v", "0", "-of", "csv=p=0", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", video_file]


        self.utils.log(color, debug_prefix, "Command to check frame_rate is: [%s]" % ' '.join(command))


        # We have to use subprocess here as os.popen doesn't catch the output correctly
        frame_rate = self.utils.command_output_subprocess(command).replace("\n", "")

        self.utils.log(color, debug_prefix, "Got frame rate output: [%s]" % frame_rate)


        # NOTE: this returns the "division" as in 2997/100 fps, or 30/1

        return frame_rate




    def get_video_info(self, video_file):

        debug_prefix = "[FFmpegWrapper.get_video_info]"

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


        return video_info


    # # # # # # # # # # # # END SESSION DEDICATED TO GETTING VIDEO INFO # # # # # # # # # # # #


    # # # # # # # # # # # # # # # SESSION DEDICATED TO VIDEO UTILS # # # # # # # # # # # # # # #



    # Extracts raw video audio into a file, copy the original stream is what it is
    def extract_raw_video_audio(self, video_file, target_output):

        # ffmpeg -i input.mkv -vn -acodec copy audio.aac

        debug_prefix = "[FFmpegWrapper.extract_video_audio]"

        command = [self.ffmpeg_binary, "-i", video_file, "-vn", "-acodec", "copy", target_output]

        #command = "\"%s\" -i \"%s\" -vn -acodec copy \"%s\"" % (self.ffmpeg_binary, video_file, target_output)

        self.utils.log(color, debug_prefix, "Extracting video audio [%s] to [%s]" % (video_file, target_output))
        self.utils.log(color, debug_prefix, "Command do do that: [%s]" % command)

        self.utils.run_subprocess(command)



    # This maps video A video and video B audio to a target video+audio
    def copy_videoA_audioB_to_other_videoC(self, get_video, get_audio, target_output):

        # ffmpeg -loglevel panic -i input_0.mp4 -i input_1.mp4 -c copy -map 0:0 -map 1:1 -shortest out.mp4

        debug_prefix = "[FFmpegWrapper.copy_video_audio_to_other_video]"

        command = [self.ffmpeg_binary, "-y", "-loglevel", "panic", "-i", get_video,
                  "-i", get_audio, "-c", "copy", "-map", "0:0", "-map", "1:1",
                  "-shortest", target_output]

        #command = "\"%s\" -loglevel panic -i \"%s\" -i \"%s\" -c copy -map 0:0 -map 1:1 -shortest \"%s\"" % (self.ffmpeg_binary, get_video, get_audio, target_output)

        self.utils.log(color, debug_prefix, "Map video [A video] and video [B audio] to a [Target C = V+A]: Video From: [%s] / Audio From: [%s] / Target to: [%s]" % (get_video, get_audio, target_output))
        self.utils.log(color, debug_prefix, "Command do do that: %s" % command)

        self.utils.run_subprocess(command)



    def apply_noise(self, input_video, output_noisey, noise):

        # ffmpeg -i input noise=c1s=8:c0f=u

        debug_prefix = "[FFmpegWrapper.apply_noise]"

        command = [self.ffmpeg_binary, "-loglevel", "warning", "-stats", "-y", "-i", input_video] + noise.split(" ") + [output_noisey]

        #command = "\"%s\" -y -i \"%s\" %s \"%s\"" % (self.ffmpeg_binary, input_video, noise, output_noisey)

        self.utils.log(color, debug_prefix, "Apply noise [%s] to [%s] and save [%s]" % (noise, input_video, output_noisey))
        self.utils.log(color, debug_prefix, "Command do do that: %s" % command)

        self.utils.log(color_by_name("li_red"), debug_prefix, "[WARNING] MAY TAKE A WHILE DEPENDING ON CPU / VIDEO LENGHT / VIDEO RESOLUTION")

        self.utils.run_subprocess(command)


    # One time pipe
    def pipe_one_time(self, output):

        debug_prefix = "[FFmpegWrapper.pipe_one_time]"

        command = [
                self.ffmpeg_binary,
                '-y',
                '-f', 'rawvideo',
                '-vcodec', 'rawvideo',
                '-s', '%sx%s' % (self.context.resolution[0]*2, self.context.resolution[1]*2),
                '-pix_fmt', 'rgb24',
                '-r', self.context.frame_rate,
                '-i', '-',
                '-an',
                '-crf', '17',
                '-vcodec', 'libx264',
                '-vf', 'pp=hb/vb/dr/fq|32, deband=range=22:blur=false',
                '-b:v', '5000k',
                output
        ]

        self.utils.log(color, debug_prefix, "Creating FFmpeg one time pipe, output [%s]" % output)

        self.pipe_subprocess = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

        self.utils.log(color, debug_prefix, "Created FFmpeg one time pipe")


    # TODO: FIGURE OUT HOW TO CONCATENATE PREVIOUS VIDEO AND PIPE NEW IMAGES ONTO A NEW ONE
    def pipe_resume(self, previous, output):

        debug_prefix = "[FFmpegWrapper.pipe_resume]"


    # Write images into pipe
    def write_to_pipe(self, image):

        debug_prefix = "[FFmpegWrapper.write_to_pipe]"

        self.pipe_subprocess.stdin.write(image)


    # Close stdin and stderr of pipe_subprocess and wait for it to finish properly
    def close_pipe(self):

        debug_prefix = "[FFmpegWrapper.close_pipe]"

        self.utils.log(color, debug_prefix, "Closing pipe")

        self.pipe_subprocess.stdin.close()
        self.pipe_subprocess.stderr.close()

        self.utils.log(color, debug_prefix, "Waiting process to finish")

        self.pipe_subprocess.wait()

        self.utils.log(color, debug_prefix, "Closed!!")




# This is a multi-class wrapper like we do with Waifu2x,
# we abstract the other class (same) functions into a single "global" class
class VideoFrameExtractor():
    def __init__(self, context, utils, controller):

        debug_prefix = "[VideoFrameExtractor.__init__]"

        self.context = context
        self.utils = utils
        self.controller = controller

        if self.context.frame_extractor_method == "cv2":
            self.utils.log(color, debug_prefix, "Method is CV2")
            self.extract = VideoFrameExtractorCV2(self.context, self.utils, self.controller)

        elif self.context.frame_extractor_method == "ffmpeg":
            self.utils.log(color, debug_prefix, "Method is FFmpeg")
            self.extract = VideoFrameExtractorFFMPEG(self.context, self.utils, self.controller)


    # Do the setup required to extract the video frames, mostly useful for CV2 method
    def setup_video_input(self, video_file):
        self.extract.setup_video_input(video_file)

    # Seek to that frame, mostly used on CV2
    def set_current_frame(self, frame_number):
        self.extract.set_current_frame(frame_number)

    # Extract the next frame on CV2, FFmpeg [TODO]
    def next_frame(self, save_location):
        self.extract.next_frame(save_location)







class VideoFrameExtractorCV2():
    def __init__(self, context, utils, controller):

        debug_prefix = "[VideoFrameExtractorCV2.__init__]"

        self.context = context
        self.utils = utils
        self.controller = controller

        self.cap = None


    # Do the setup required to extract the video frames, mostly useful for this class
    def setup_video_input(self, video_file):

        debug_prefix = "[VideoFrameExtractorCV2.setup_video_input]"

        self.cap = cv2.VideoCapture(video_file)

        if self.cap.isOpened() == False:
            self.utils.log(color_by_name("li_red"), debug_prefix, "[ERROR] Couldn't open video capture")
            self.utils.exit()

        if self.context.extracted_images_extension == ".png":
            self.utils.log(color_by_name("li_red"), debug_prefix, "[WARNING] PNG SET TO EXTRACTED IMAGES WITH OPENCV, IT'S ABOUT 4X SLOWER THAN JPG")



    # Seek to that frame_number
    def set_current_frame(self, frame_number):

        debug_prefix = "[VideoFrameExtractorCV2.set_current_frame]"

        self.utils.log(color, debug_prefix, "Setting current frame to [%s]" % frame_number)

        self.cap.set(1, frame_number)



    # Extract the next frame
    def next_frame(self, save_location):

        debug_prefix = "[VideoFrameExtractorCV2.next_frame]"

        # Cap not set
        if self.cap == None:
            self.utils.log(color_by_name("li_red"), debug_prefix, "[ERROR] No video cap set")
            self.utils.exit()

        # Hard debug
        if self.context.loglevel >= 4:
            self.utils.log(color, debug_prefix, "Asking new frame, N=[%s], saving to [%s]" % (self.context.last_processing_frame, save_location))

        # Actually get the frame
        sucess, frame = self.cap.read()


        if sucess == False:
            self.utils.log(color_by_name("li_red"), debug_prefix, "[WARNING] Cannot read more frames or out of frames??")

        else:
            if self.context.extracted_images_extension == ".png":
                cv2.imwrite(save_location, frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])

            if self.context.extracted_images_extension == ".jpg":
                cv2.imwrite(save_location, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

            self.context.last_processing_frame += 1








class VideoFrameExtractorFFMPEG():
    def __init__(self, context, utils, controller):

        debug_prefix = "[VideoFrameExtractorFFMPEG.__init__]"

        self.context = context
        self.utils = utils
        self.controller = controller

    def setup_video_input(self, video_file):
        pass
















class Video():
    def __init__(self, context, utils, controller):

        debug_prefix = "[Video.__init__]"

        self.context = context
        self.utils = utils
        self.controller = controller

        self.ROOT = self.context.ROOT

        self.ffmpeg = FFmpegWrapper(self.context, self.utils, self.controller)
        self.frame_extractor = VideoFrameExtractor(self.context, self.utils, self.controller)

        self.utils.log(color, debug_prefix, "Init")


    # TODO: Should be moved into its own class?
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

        self.utils.log(color, debug_prefix, "Video file is: [%s]" % self.context.input_file)


        # Get the video info

        if self.context.get_video_info_method == "mediainfo":
            self.get_video_info_with_mediainfo(self.context.input_file)

        elif self.context.get_video_info_method == "ffmpeg":
            self.get_video_info_with_ffmpeg(self.context.input_file)

        else:
            self.utils.log(color_by_name("li_red"), debug_prefix, "[ERROR] NO VALID get_video_info_method SET: [%s]" % self.context.get_video_info_method)
            self.utils.exit()


        # # Save info to context

        self.resolution = [self.width, self.height]

        self.context.resolution = self.resolution
        self.context.height = self.height
        self.context.width = self.width

        self.context.frame_count = self.frame_count
        self.context.frame_rate = self.frame_rate

        # We change how much zero padding we have based on the digit count of the frame_count, plus 1 to be safe
        self.context.zero_padding = len(str(self.context.frame_count)) + 1
        self.utils.log(color, debug_prefix, "Changing zero padding in files to [%s]" % self.context.zero_padding)




    # Self explanatory
    def show_info(self):

        debug_prefix = "[Video.show_info]"

        self.utils.log(color, debug_prefix, "Here's the video info:")

        self.utils.log(color, self.context.indentation, "ABS Path: [%s]" % self.context.input_file)
        self.utils.log(color, self.context.indentation, "Resolution: (%sx%s)" % (self.width, self.height))
        self.utils.log(color, self.context.indentation, "Frame count: [%s]" % self.frame_count)
        self.utils.log(color, self.context.indentation, "Frame rate: [%s]" % self.frame_rate)



    def apply_noise(self, input_video, output_noisey, noise):
        self.ffmpeg.apply_noise(input_video, output_noisey, noise)
