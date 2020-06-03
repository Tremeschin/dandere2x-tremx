"""
===============================================================================

Purpose: Deals with building the final video according to the C++ data we get
from the block matching

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

import threading
import math
import time
import copy
import os


color = colors["processing"]


class Processing():
    def __init__(self, context, utils, controller, frame, video, upscaler):

        debug_prefix = "[Processing.__init__]"

        self.context = context
        self.utils = utils
        self.controller = controller
        self.frame = frame
        self.video = video
        self.upscaler = upscaler

    # A generator which gives us the vectors for iterating over the upscaled residual
    def residual_vector_iterator_generator(self, columns, rows, width, height, bleed, block_size):

        debug_prefix = "[Processing.residual_vector_iterator_generator]"

        # Bleed and block size has been upscaled by upscale ratio
        bleed *= self.context.upscale_ratio
        block_size *= self.context.upscale_ratio

        # Bleeded block size: [O] - bleed, [X] - original data
        """
        O O O O O
        O X X X O
        O X X X O
        O X X X O
        O O O O O
        """
        # You can see it has the block size on the middle and two extra bleeded parts on opposite side
        # An upscaled residual would look something like this (a 4x4 grid):
        """
        O O O O O O O O O O
        O X X X O O X X X O
        O X X X O O X X X O
        O X X X O O X X X O
        O O O O O O O O O O
        O O O O O O O O O O
        O X X X O O X X X O
        O X X X O O X X X O
        O X X X O O X X X O
        O O O O O O O O O O
        """
        bleeded_block_size = block_size + (2*bleed)

        # Numpy arrays are [V[H, H, H], V[H, H, H], V[H, H, H]] so the vertical iteration is first (top->bottom)
        for y in range(rows):

            # The Y coordinate the bleed-removed block (only original data upscaled) starts
            start_y = bleed + (bleeded_block_size * y)

            # Then iterate on the horizontal
            for x in range(columns):

                # The X coordinate the bleed-removed block (only original data upscaled) starts
                start_x = bleed + (bleeded_block_size * x)

                # Hard debug on loglevel 10
                self.utils.log(color, 10, debug_prefix, "Yielding: [%s, %s]" % (start_y, start_x))

                # Yield these starting coordinates
                yield (start_y, start_x)

    # Main routine on merging frames
    def run(self):

        debug_prefix = "[Processing.run]"

        # Create two frame classes, one to load the upscaled residuals and other that is the 
        # start_frame which will become the merged frame
        residual_upscaled = self.frame(self.context, self.utils, self.controller)
        start_frame = self.frame(self.context, self.utils, self.controller)

        # Create new blank start_frame as that's we start with
        start_frame.new(
            self.context.resolution[0] * self.context.upscale_ratio,
            self.context.resolution[1] * self.context.upscale_ratio
        )

        # We're resuming here so the start_frame is the last frame of the last partial video file
        if self.context.last_processing_frame > 0:
            # Load the resume video frame
            start_frame.load_from_path_wait(self.context.resume_video_frame)
            
        # The self.merged object is now the start_frame
        # NOTE: start_frame is NOT the image but the Frame() class
        self.merged = start_frame

        # For each frame since the one we started with
        frame_number = self.context.last_processing_frame

        # Main routine
        while True:

            # Wait for next upscale file to exist or quit if controller says so
            while True:
                if self.controller.stop == True:
                    self.utils.log(color, 1, debug_prefix, "Stopping processing as controller stop is True")
                    return 0
                if str(frame_number) in self.controller.block_match_data:
                    break
                if frame_number == self.context.frame_count:
                    break
                
                self.utils.log(color, 7, debug_prefix, "Waiting for frame_number [%s] in controller.block_match_data" % frame_number)
                time.sleep(0.5)

            # Get the full working data
            working_data = self.controller.block_match_data[str(frame_number)]

            # Break it onto the vector IDs and "processing frame" type C++ told us
            working_vector_ids = working_data["data"] 
            working_type = working_data["type"]

            # Delete the data on the dictionary as we don't need it anymore
            # We generate a new one when resuming anyways
            del self.controller.block_match_data[str(frame_number)]

            # Haard debug
            self.utils.log(color, 9, debug_prefix, "[%s] Working vector ids:" % frame_number)
            self.utils.log(color, 9, debug_prefix, working_vector_ids)

            # Type "empty" nothing needs to be done
            if working_type == "empty":
                pass
            
            # Here we have to load a new upscaled residual so both "blocks" and "fullframe"
            elif (working_type in ["blocks", "fullframe"]):
                
                self.utils.log(color, 8, debug_prefix, "Merged image is from upscaled residual")

                # Each upscaler outputs the images in a different naming sadly
                residual_upscaled_file_path = self.upscaler.get_residual_upscaled_file_path_output_frame_number(frame_number)

                # Load the next upscaled images
                residual_upscaled.load_from_path_wait(residual_upscaled_file_path)

                if self.controller.stop:
                    self.utils.log(color, 1, debug_prefix, "Quitting as controller said to stop")
                    return 0

                # We upscaled the full frame as it has passed the threshold, so the merged.frame is the upscaled frame
                elif working_type == "fullframe":
                    self.utils.log(color, 8, debug_prefix, "Type is fullframe, merged is residual_upscaled")
                    self.merged.frame = residual_upscaled.frame

                # We have blocks to substitute
                # This is the process we build back the images from the upscaled residuals
                elif working_type == "blocks":
                
                    residual_dimensions = (residual_upscaled.width, residual_upscaled.height)

                    # As we trim the bottom black portion of the image, there can be some weird blocks like
                    # 44x48 resolution, so whenever that happens we just get the ceil of that number
                    # as it'll be 0 < x < 1 for a (1, 1) block grid where 1 is x
                    grid_dimensions = [
                        math.ceil(
                            (residual_dimensions[0]/self.context.upscale_ratio) / ((2*self.context.bleed) + self.context.block_size)
                        ),
                        math.ceil
                            ((residual_dimensions[1]/self.context.upscale_ratio) / ((2*self.context.bleed) + self.context.block_size)
                        )
                    ]

                    # Gets the generator which will yield for us the iterations and coordinates of the block on the residual upscaled
                    # columns, rows, width, height, bleed, block_size
                    this_residual_vector_generator = \
                        self.residual_vector_iterator_generator(
                            grid_dimensions[0],
                            grid_dimensions[1],
                            residual_dimensions[0],
                            residual_dimensions[1],
                            self.context.bleed,
                            self.context.block_size
                        )

                    # Loop every block vector we have to replace
                    for vector_id in working_vector_ids:

                        # Get the next starting coordinate of the block in the upscaled residual                        
                        residual_get_vector = next(this_residual_vector_generator)

                        # Where this block will go on the merged frame
                        position_where_vector = self.controller.vectors[vector_id]

                        # ULTRA SLOW DEBUG
                        self.utils.log(color, 10, debug_prefix, "residual vector: ", residual_get_vector)
                        self.utils.log(color, 10, debug_prefix, "position vector: ", position_where_vector)

                        # Use our data to make the merged image
                        # See https://stackoverflow.com/questions/52702809/copy-array-into-part-of-another-array-in-numpy
                        # For more information on this function
                        self.merged.copy_from(

                            residual_upscaled.frame,
                            self.merged.frame,

                            [residual_get_vector[0], residual_get_vector[1]],
                            
                            [
                                position_where_vector[0]*self.context.upscale_ratio,
                                position_where_vector[1]*self.context.upscale_ratio
                            ], 
                            
                            [
                                (position_where_vector[2]*self.context.upscale_ratio) - 1,
                                (position_where_vector[3]*self.context.upscale_ratio) - 1
                            ]
                        )

                        # See the blocks being completed, useful for debug
                        # self.merged.save("merged/merged_frame_%s_vector_%s.png" % (frame_number, vector_id))

            else:
                # No vectors to substitute and is not fullframe, "end" type, quit main loop
                if working_type == "end":
                    self.utils.log(color, 8, debug_prefix, "Writing the same previous merged frame as working_type==exit")
                    break
                
                self.utils.log(color, 8, debug_prefix, "Writing the same previous merged frame as vectors==null")
            
            # # Write self.merged into the FFmpeg pipe and change variables accordingly

            self.utils.log(color, 8, debug_prefix, "Writing merged image into pipe n=[%s]" % frame_number)

            # self.merged.save("merged/merged_frame_%s.png" % frame_number)
            # self.merged.save("merged/merged.png")

            # Write the self.merged.frame to the encoding pipe
            self.video.ffmpeg.write_to_pipe(self.merged.frame)
            
            self.utils.log(color, 8, debug_prefix, "Wrote merged frame")

            # Update the last processed frame for ruthless_residual_eliminator to act and mindisk C++ to be free
            self.context.last_processing_frame = frame_number            

            self.utils.log(color, 8, debug_prefix, "Context last_processing_frame is now [%s]" % self.context.last_processing_frame)

            # If Dandere2x / computer crashes or power goes off, hopefully we can continue the upscale?
            self.utils.log(color, 8, debug_prefix, "[FAILSAFE] Saving context vars if Dandere2x crashes")
            self.context.save_vars()

            frame_number += 1

        # # # # OUT OF MAIN LOOP # # # #

        self.utils.log(color, 1, debug_prefix, "All merged images done, closing pipe")

        # Finished piping all the images we merged
        self.video.ffmpeg.close_pipe()

        # Upscale finished, goodbye Dandere!!
        self.controller.upscale_finished = True
        self.controller.exit()


if __name__ == "__main__":
    print("You shouldn't be running this file directly, Dandere2x is class based and those are handled by dandere2x.py which is controlled by dandere2x_cli.py or the upcoming GUI")
