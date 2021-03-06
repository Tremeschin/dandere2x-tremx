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

from color import colors
from PIL import Image
import subprocess
import time
import copy
import cv2
import sys
import os


color = colors["video"]


class FFmpegWrapper():
    def __init__(self, context, utils, controller):

        debug_prefix = "[FFmpegWrapper.__init__]"

        self.context = context
        self.utils = utils
        self.controller = controller

        self.ffmpeg_binary = self.utils.get_binary("ffmpeg")
        self.ffprobe_binary = self.utils.get_binary("ffprobe")


    # # # # # # # # # # # # # SESSION DEDICATED TO GETTING VIDEO INFO # # # # # # # # # # # # #

    # One way of getting the video frame count, output -f null
    def get_frame_count_with_null_copy(self, video_file):

        # ffmpeg -i input.mkv -map 0:v:0 -c copy -f null -

        debug_prefix = "[FFmpegWrapper.get_frame_count_with_null_copy]"

        self.utils.log(color, 1, debug_prefix, "[WARNING] CHECKING VIDEO FRAME COUNT SAFE WAY, MAY TAKE A WHILE DEPENDING ON CPU AND VIDEO LENGTH")

        # Build the command to get the frame_count with "null copy" mode
        command = ["%s" % self.ffmpeg_binary, "-loglevel", "warning", "-stats", "-i", "%s" % video_file, "-map", "0:v:0", "-c", "copy", "-f", "null", "-"]

        self.utils.log(color, 5, debug_prefix, "Command to check frame_count is: [%s]" % ' '.join(command))

        # We have to use subprocess here as os.popen doesn't catch the output correctly
        info = self.utils.command_output_subprocess(command)
        frame_count = None

        self.utils.log(color, 6, debug_prefix, "[DEBUG] COMMAND OUTPUT:")
        self.utils.log(colors["white"], 6, debug_prefix, info)

        # Iterate through the output lines
        for line in info.split("\n"):
            if "frame=" in line:

                self.utils.log(color, 4, debug_prefix, "Line with \"frames=\" in it: [%s]" % line)

                # Transform every non single whitespace to one single whitespace
                line = ' '.join(line.split())

                frame_count = line.split("fps")[0].split("=")[1]
                frame_count = int(frame_count)

                self.utils.log(color, 2, debug_prefix, "Got frame count: [%s]" % frame_count)

        # Fail safe
        if frame_count == None:
            self.utils.log(colors["error"], 0, debug_prefix, "[ERROR] COULDN'T GET FRAME COUNT")
            self.controller.exit()

        return frame_count

    # Use FFprobe and its process output for getting the resolution
    def get_resolution_with_ffprobe(self, video_file):

        # ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of default=nw=1 input.mp4

        debug_prefix = "[FFmpegWrapper.get_resolution_with_ffprobe]"

        wanted = {
            "width": None,
            "height": None
        }

        command = [self.ffprobe_binary, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "default=nw=1", video_file]

        self.utils.log(color, 5, debug_prefix, "Command to check resolution is: [%s]" % ' '.join(command))

        # We have to use subprocess here as os.popen doesn't catch the output correctly
        info = self.utils.command_output_subprocess(command)

        self.utils.log(color, 6, debug_prefix, "[DEBUG] COMMAND OUTPUT:")
        self.utils.log(colors["white"], 6, debug_prefix, info)

        # Iterate in the output lines
        for line in info.split("\n"):

            line = line.replace("\n", "")

            # Parse the line

            if "width" in line:
                self.utils.log(color, 5, debug_prefix, "Line with width: [%s]" % line)

                wanted["width"] = int(line.split("=")[1])

            if "height" in line:
                self.utils.log(color, 5, debug_prefix, "Line with height: [%s]" % line)

                wanted["height"] = int(line.split("=")[1])

        self.utils.log(color, 2, debug_prefix, "Got width: [%s] and height: [%s]" % (wanted["width"], wanted["height"]))

        return wanted

    # Use FFprobe and its process output for getting the frame rate
    def get_frame_rate_with_ffprobe(self, video_file):

        # ffprobe -v 0 -of csv=p=0 -select_streams v:0 -show_entries stream=r_frame_rate infile
        # NOTE: this returns the "division" as in 2997/100 fps, or 30/1

        debug_prefix = "[FFmpegWrapper.get_resolution_with_ffprobe]"

        command = [self.ffprobe_binary, "-v", "0", "-of", "csv=p=0", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", video_file]

        self.utils.log(color, 5, debug_prefix, "Command to check frame_rate is: [%s]" % ' '.join(command))

        # We have to use subprocess here as os.popen doesn't catch the output correctly
        frame_rate = self.utils.command_output_subprocess(command).replace("\n", "").replace("\r", "")

        self.utils.log(color, 2, debug_prefix, "Got frame rate output: [%s]" % frame_rate)

        return frame_rate

    # Get the video info based on user choice in settings.yaml
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
        if self.context.get_frame_count_method == "null_copy" and not self.context.write_debug_video:
            self.utils.log(color,3,  debug_prefix, "[INFO] Getting video [frame_count] info with [NULL COPY] method")
            video_info["frame_count"] = self.get_frame_count_with_null_copy(video_file)

        # Get the resolution
        if self.context.get_resolution_method == "ffprobe":
            self.utils.log(color, 3, debug_prefix, "[INFO] Getting video [resolution] info with [ffprobe] method")
            resolution = self.get_resolution_with_ffprobe(video_file)
            video_info["width"] = resolution["width"]
            video_info["height"] = resolution["height"]

        # Get the frame rate
        if self.context.get_frame_rate_method == "ffprobe":
            self.utils.log(color, 3, debug_prefix, "[INFO] Getting video [frame_rate] info with [ffprobe] method")
            video_info["frame_rate"] = self.get_frame_rate_with_ffprobe(video_file)

        return video_info

    # # # # # # # # # # # # END SESSION DEDICATED TO GETTING VIDEO INFO # # # # # # # # # # # #


    # # # # # # # # # # # # # # # SESSION DEDICATED TO VIDEO UTILS # # # # # # # # # # # # # # #

    # This maps video A video and video B audio to a target video+audio
    def copy_videoA_audioB_to_other_videoC(self, get_video, get_audio, target_output):

        # ffmpeg -loglevel panic -i input_0.mp4 -i input_1.mp4 -c copy -map 0:0 -map 1:1 -shortest out.mp4

        debug_prefix = "[FFmpegWrapper.copy_video_audio_to_other_video]"

        command = [self.ffmpeg_binary, "-y", "-loglevel", "panic", "-i", get_video,
                  "-i", get_audio, "-c", "copy", "-map", "0:0", "-map", "1:1",
                  "-shortest", target_output]

        self.utils.log(color, 2, debug_prefix, "Map video [A video] and video [B audio] to a [Target C = V+A]: Video From: [%s] / Audio From: [%s] / Target to: [%s]" % (get_video, get_audio, target_output))
        self.utils.log(color, 5, debug_prefix, "Command do do that: %s" % command)

        self.utils.run_subprocess(command)

    # Calls a FFmpeg process reading images from stdin
    # This can't be reutilized so we save to a partial video file
    def pipe_one_time(self, output):

        debug_prefix = "[FFmpegWrapper.pipe_one_time]"

        command = [
                self.ffmpeg_binary,
                '-loglevel', 'panic',
                '-nostats',
                '-hide_banner',
                '-y',
                '-f', "image2pipe",
                #'-f', 'rawvideo',
                #'-vcodec', 'rawvideo',
                #'-video_size', '%sx%s' % (self.context.resolution[0]*self.context.upscale_ratio, self.context.resolution[1]*self.context.upscale_ratio),
                #'-pix_fmt', 'rgb24',
                #'-color_range', '2',
                #'-r', self.context.frame_rate,
                '-i', '-',
                '-an',
                '-c:v', self.context.encode_codec,
                '-crf', str(self.context.x264_crf),
                '-preset', self.context.x264_preset,
                '-vf', self.context.deblock_filter,
                #'-vf', 'format=yuvj444p',
                '-pix_fmt', 'yuv420p',
                '-color_range', 'jpeg',
                '-r', self.context.frame_rate
        ]

        if not self.context.x264_tune == None:
            command += ['-tune', self.context.x264_tune]
        
        command += [output]

        self.utils.log(color, 1, debug_prefix, "Creating FFmpeg one time pipe, output [%s]" % output)

        self.utils.log(color, 5, debug_prefix, "Full command is: [%s]" % command)

        self.pipe_subprocess = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8, cwd=os.path.dirname(self.ffmpeg_binary))

        self.utils.log(color, 3, debug_prefix, "Created FFmpeg one time pipe")

        self.stop_piping = False
        self.lock_writing = False
        self.images_to_pipe = []

    # Write images into pipe
    def write_to_pipe(self, image):
        self.images_to_pipe.append(copy.deepcopy(image.image_array()))
        #self.pipe_subprocess.stdin.write(image)

    # Thread save the images to the pipe, this way processing.py can do its job while we write the images
    def pipe_writer_loop(self):

        debug_prefix = "[FFmpegWrapper.pipe_writer_loop]"

        count = 0

        while not self.stop_piping:
            if len(self.images_to_pipe) > 0:
                self.lock_writing = True
                image = self.images_to_pipe.pop(0)
                image.save(self.pipe_subprocess.stdin, format="jpeg", quality=100)
                self.lock_writing = False
            else:
                time.sleep(0.1)

            count += 1

            self.utils.log(color, 8, debug_prefix, "Write new image from buffer to pipe, count=[%s]" % count)

    # Close stdin and stderr of pipe_subprocess and wait for it to finish properly
    def close_pipe(self):

        debug_prefix = "[FFmpegWrapper.close_pipe]"

        self.utils.log(color, 1, debug_prefix, "Closing pipe")

        while not len(self.images_to_pipe) == 0:
            self.utils.log(color, 1, debug_prefix, "Waiting for image buffer list to end, len [%s]" % len(self.images_to_pipe))
            time.sleep(0.1)

        while self.lock_writing:
            self.utils.log(color, 1, debug_prefix, "Lock writing is on, should only have one image?")
            time.sleep(0.1)

        self.stop_piping = True
        self.pipe_subprocess.stdin.close()
        self.pipe_subprocess.stderr.close()

        self.utils.log(color, 3, debug_prefix, "Waiting process to finish")

        self.pipe_subprocess.wait()

        self.utils.log(color, 3, debug_prefix, "Closed!!")


    def concat_video_folder_reencode(self, folder, output):

        debug_prefix = "[FFmpegWrapper.cocat_video_folder]"

        self.utils.log(color, 2, debug_prefix, "Concatenating partials and reencoding")

        files = os.listdir(folder)

        # Sort the files numerically
        files = [int(x.replace(".mkv", "")) for x in files]
        files.sort()
        files = [str(x) + ".mkv" for x in files]

        how_much_files = len(files)

        files_path = [folder + file for file in files]

        command = [self.ffmpeg_binary, "-y"]

        # Set input to every file
        for file_path in files_path:
            command += ["-i", file_path]

        command += ['-filter_complex']

        concat_option = ""

        for i in range(how_much_files):
            concat_option += "[%s:v] " % i

        concat_option += "concat=n=%s:v=1 [v] " % how_much_files

        command += [concat_option]
        command += ["-map", "[v]"]
        command += [output]

        self.utils.log(color, 5, debug_prefix, "Command to merge partials:")
        self.utils.log(color, 5, debug_prefix, command)

        self.utils.run_subprocess(command)


    def save_last_frame_of_video(self, video, output):
        # ffmpeg -sseof -3 -i input -update 1 -q:v 1 last.jpg

        debug_prefix = "[FFmpegWrapper.save_last_frame_of_video_ffmpeg]"

        command = [self.ffmpeg_binary, "-y", "-sseof", '-1', '-i', video, '-update', '1', '-q:v', '1', output]

        self.utils.log(color, 5, debug_prefix, "Command to save last frame:")
        self.utils.log(color, 5, debug_prefix, command)

        self.utils.run_subprocess(command)


# The class which abstracts many useful video functions
class Video():
    def __init__(self, context, utils, controller):

        debug_prefix = "[Video.__init__]"

        self.context = context
        self.utils = utils
        self.controller = controller

        self.ROOT = self.context.ROOT

        self.ffmpeg = FFmpegWrapper(self.context, self.utils, self.controller)

    def save_last_frame_of_video_ffmpeg(self, video, output):
        self.ffmpeg.save_last_frame_of_video(video, output)

    # Get the last video frame of a given input
    def save_last_frame_of_video_cv2(self, video, output):

        debug_prefix = "[Video.save_last_frame_of_video]"

        self.utils.log(color, 1, debug_prefix, "Saving last frame of video [%s] to [%s]" % (video, output))

        capture = cv2.VideoCapture(video)

        while True:
            success, frame = capture.read()
            if not success:
                break

        cv2.imwrite(output, frame)


    # TODO: Should be moved into its own class?
    def get_video_info_with_mediainfo(self, video_path):

        debug_prefix = "[Video.get_video_info_with_mediainfo]"

        self.utils.log(color, 2, debug_prefix, "Using mediainfo to get video info")

        # What output we want from mediainfo, and run it
        output_format = r'--Output="Video;%FrameCount%,%FrameRate%,%Width%,%Height%"'
        command = "%s --fullscan %s \"%s\"" % (self.utils.get_binary("mediainfo"), output_format, video_path)

        self.utils.log(color, 5, debug_prefix, "Command to get info is: [%s]" % command)

        out = self.utils.command_output(command).replace("\n", "")

        self.utils.log(color, 5, debug_prefix, "Got output: [%s]" % out)

        # Remove the new line and split by commas
        out = out.split(",")

        # # Set variables
        self.utils.log(color, 5, debug_prefix, "Got info, setting vars")

        # Frame
        self.frame_count = int(out[0])
        self.frame_rate = float(out[1])

        # Resolution
        self.width = int(out[2])
        self.height = int(out[3])

        self.resolution = [self.width, self.height]

    # Get video information with FFprobe
    def get_video_info_with_ffmpeg(self, video_path):

        debug_prefix = "[Video.get_video_info_with_ffprobe]"

        video_info = self.ffmpeg.get_video_info(video_path)

        # Frame
        self.frame_count = video_info["frame_count"]
        self.frame_rate = video_info["frame_rate"]

        # Resolution
        self.width = video_info["width"]
        self.height = video_info["height"]

    # Get video info with the method the user have chosen
    def get_video_info(self):

        debug_prefix = "[Video.get_video_info]"

        self.utils.log(color, 1, debug_prefix, "Video file is: [%s]" % self.context.input_file)

        # Get the video info

        if self.context.get_video_info_method == "mediainfo":
            self.get_video_info_with_mediainfo(self.context.input_file)

        elif self.context.get_video_info_method == "ffmpeg":
            self.get_video_info_with_ffmpeg(self.context.input_file)

        else:
            self.utils.log(colors["error"], 0, debug_prefix, "[ERROR] NO VALID get_video_info_method SET: [%s]" % self.context.get_video_info_method)
            self.controller.exit()

        # # Save info to context

        self.resolution = [self.width, self.height]

        self.context.resolution = self.resolution
        self.context.height = self.height
        self.context.width = self.width

        self.context.frame_count = self.frame_count
        self.context.frame_rate = self.frame_rate

        # We change how much zero padding we have based on the digit count of the frame_count, plus 1 to be safe
        self.context.zero_padding = len(str(self.context.frame_count)) + 1
        self.utils.log(color, 4, debug_prefix, "Changing zero padding in files to [%s]" % self.context.zero_padding)

    # Self explanatory, show video info
    def show_info(self):

        debug_prefix = "[Video.show_info]"

        self.utils.log(color, 3, debug_prefix, "Here's the video info:")

        self.utils.log(color, 3, self.context.indentation, "ABS Path: [%s]" % self.context.input_file)
        self.utils.log(color, 3, self.context.indentation, "Resolution: (%sx%s)" % (self.width, self.height))
        self.utils.log(color, 3, self.context.indentation, "Frame count: [%s]" % self.frame_count)
        self.utils.log(color, 3, self.context.indentation, "Frame rate: [%s]" % self.frame_rate)

if __name__ == "__main__":
    from utils import Miscellaneous
    Miscellaneous()
    print("You shouldn't be running this file directly, Dandere2x is class based and those are handled by dandere2x.py which is controlled by dandere2x_cli.py or the upcoming GUI")
