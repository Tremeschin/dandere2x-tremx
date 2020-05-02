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


from color import rgb, debug_color

import threading
import time
import copy
import os

color = rgb(0, 115, 255)

class Processing():
    def __init__(self, context, utils, controller, frame, video):

        debug_prefix = "[Processing.__init__]"

        self.context = context
        self.utils = utils
        self.controller = controller
        self.frame = frame
        self.video = video

    '''
    start_x = (x * block_size);
    end_x = start_x + block_size;

    // If x it surpasses the width
    end_x = std::min(width, end_x);


    for (int y=0; y < height_iterations; y++) {

        start_y = (y * block_size);
        end_y = start_y + block_size;

        // If y it surpasses the height
        end_y = std::min(height, end_y);
    '''


    def residual_vector_iterator_generator(self, columns, rows, width, height, bleed, block_size):

        bleed *= 2
        block_size *= 2

        for y in range(rows):

            start_y = bleed + (y * (bleed + block_size))
            end_y = min(height, start_y + block_size)

            for x in range(columns):

                start_x = bleed + (x * (bleed + block_size))
                end_x = min(width, start_x + block_size)

                yield (start_y, start_x, end_y, end_x)



    def run(self):

        # TODO: WAIT FOR CPP CONTENTS
        time.sleep(2)

        debug_prefix = "[Processing.run]"

        residual_upscaled = copy.copy(self.frame)
        start_frame = copy.copy(self.frame)

        start_frame.new(self.context.resolution[0] * 2, self.context.resolution[1] * 2)

        if self.context.last_processing_frame > 0:
            # TODO: get the last video frame from the partial upscale
            pass

        merged = start_frame

        # For each frame since the one we started with
        for frame_number in range(self.context.last_processing_frame, self.context.frame_count - 1):

            # Wait for file to exist or quit if controller says so
            while True:
                if self.controller.stop is True:
                    return 0
                if str(frame_number) in self.controller.block_match_data:
                    break
                self.utils.log(color, debug_prefix, "Waiting for frame_number [%s] in controller.block_match_data" % frame_number)
                time.sleep(0.5)


            # print(self.controller.block_match_data)

            working_data = self.controller.block_match_data[str(frame_number)]
            working_vector_ids = working_data["data"].split(";")

            # print("working_data", working_data)
            # print("vector ids", working_vector_ids)

            if working_data["type"] == "pframe":

                residual_upscaled_file_path = self.context.upscaled + os.path.sep + "residual_" + self.utils.pad_zeros(frame_number) + ".jpg.png"
                residual_file_path = self.context.residual + os.path.sep + "residual_" + self.utils.pad_zeros(frame_number) + ".jpg"
                residual_upscaled.load_from_path_wait(residual_upscaled_file_path)

                dimensions = (residual_upscaled.width, residual_upscaled.height)

                grid_dimensions = [
                    int(((dimensions[0] - (self.context.bleed*2)) / (self.context.bleed + self.context.block_size))/2),
                    int(((dimensions[1] - (self.context.bleed*2)) / (self.context.bleed + self.context.block_size))/2)
                ]


                # columns, rows, width, height, bleed, block_size
                this_residual_vector_generator = \
                    self.residual_vector_iterator_generator(
                        grid_dimensions[0],
                        grid_dimensions[1],
                        dimensions[0],
                        dimensions[1],
                        self.context.bleed,
                        self.context.block_size
                    )

                # print("---")
                #if self.context.loglevel >= 7:
                    #self.utils.log(color, debug_prefix, "Grid dimensions: " + ' '.join(grid_dimensions))
                # print("Grid dimensions: ", grid_dimensions)

                for vector_id in working_vector_ids:
                    residual_get_vector = next(this_residual_vector_generator)
                    position_where_vector = self.controller.vectors[vector_id]

                    # print("vectors: ", self.controller.vectors)
                    # print("vector id: ", vector_id)

                    # print("Position where vector: ", position_where_vector)
                    # print("Residual vector: ", residual_get_vector)


                    """
                    copy_from(self, A, B, A_start, B_start, B_end)
                    A_start is the index with respect to A of the upper left corner of the overlap
                    B_start is the index with respect to B of the upper left corner of the overlap
                    B_end is the index of with respect to B of the lower right corner of the overlap
                    """


                    merged.copy_from(
                        residual_upscaled.frame,
                        merged.frame,
                        [ residual_get_vector[0],   residual_get_vector[1]   ],
                        [ position_where_vector[1], position_where_vector[0] ],
                        [ position_where_vector[3], position_where_vector[2] ]
                    )

                    #merged.save("merged_vector%s.png" % vector_id)

                merged.save(self.context.merged + "merged_%s.jpg" % self.utils.pad_zeros(frame_number))

                # Update the last processed frame for resume session
                self.context.last_processing_frame = frame_number

                self.utils.delete_file(residual_file_path)
