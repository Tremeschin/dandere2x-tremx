"""
===============================================================================

Purpose: Utilities to get and show ETAs, averages for a Dandere2x session

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

# Only raw ported to Dandere2x Tremx, needs rewriting / less confusing programming

from color import colors
import datetime
import random
import time
import math


color = colors["stats"]


class Dandere2xStats():

    def __init__(self, context, utils, controller):

        debug_prefix = "[Core.__init__]"

        self.context = context
        self.utils = utils
        self.controller = controller

        self.frame_times = [0 for _ in range(self.context.average_last_N_frames)]

        self.precision = 4

        self.recycled_percentage = 0

    def start(self):

        debug_prefix = "[Dandere2xStats.start]"

        self.time_start = time.time()
        self.last_time_completed = self.time_start  # for calculating the ETA correctly

        last_frame = self.context.last_processing_frame

        while not self.controller.stop:
            
            self.controller.stats_list = self.get_stats_text(self.context.last_processing_frame, self.context.frame_count)

            for item in self.controller.stats_list:
                print(item)
            
            print()

            while last_frame == self.context.last_processing_frame:
                time.sleep(0.01)
            
            last_frame = self.context.last_processing_frame

    # Lazy math
    def proportion(self, a, b, c):
        # a is to b
        # c is to what
        # what = b*c/a
        if a == 0:
            return 0
        return b*c/a

    # This needs to be called outside of this class preferably in a separate thread
    def get_stats_text(self, currentframe, totalframes):

        currentframe += 1

        # For calculating global averages
        time_took_until_now = time.time() - self.time_start

        # Percentage of completion
        percentage_completed = self.proportion(totalframes, 100, currentframe)
        self.controller.percentage_completed = round(percentage_completed, 2)

        # The text to set the progressbar to
        progress_text = f"Progress: Frame [{currentframe}/{totalframes}]  [Recycled blocks: {self.recycled_percentage}%]"

        # Put the values it took to go to the next frame based on the
        # difference of last item to the current one, that's being looped
        # by the modulo operation since it's the remainder of smth
        self.frame_times[ currentframe % self.context.average_last_N_frames ] = time.time() - self.last_time_completed
        self.last_time_completed = time.time()

        #    AVERAGES

        # Get the 10 last items by "biasing" the currentframe, sum those numbers and divide by 10
        # do not consider those who are zero otherwise wrong average value
        

        average_10_list = self.frame_times[ (currentframe - 10) % self.context.average_last_N_frames : currentframe % self.context.average_last_N_frames ]

        average_10_denominator = 10 - average_10_list.count(0)

        if not average_10_denominator == 0:
            average_last_10 =  sum(average_10_list)/(average_10_denominator)
            average_last_10 = "%.4f" % average_last_10
        else:
            average_last_10 = "NaN"

        # Just sum it up and divide by n_frames_average
        average_last_n_empty_spaces = self.context.average_last_N_frames - self.frame_times.count(0)

        if not average_last_n_empty_spaces == 0:
            average_last_n = sum(self.frame_times) / (average_last_n_empty_spaces)
            average_last_n = f"%.{self.precision}f" % average_last_n
        else:
            average_last_n = "NaN"


        # Self explanatory I guess?
        average_all = time_took_until_now / currentframe

        if average_all == 0:
            fps = "NaN"
        else:
            fps = f"%.{self.precision}f" % (1/average_all)

        
        
        average_all_round = f"%.{self.precision}f" % average_all

        # The text to set the widget to
        average_text = f"Average last N frames:  [10: {average_last_10} sec/frame]  [{self.context.average_last_N_frames}: {average_last_n} sec/frame]  [ALL: {average_all_round} sec/frame = {fps} fps]"


        #   ETA

        # Basic proportion on how much time left until completion

        eta_time_number = average_all*(totalframes-currentframe)
        eta_time = str(datetime.timedelta(seconds=round(eta_time_number, 2)))[:-7]

        tt_time = time_took_until_now
        tt_time = str(datetime.timedelta(seconds=round(time_took_until_now,2)))[:-5]

        now_plus_eta = str(datetime.datetime.now() + datetime.timedelta(seconds = eta_time_number))[:-7]

        eta_text = f"Total Time: [{tt_time}]  EST: [{eta_time}] --> Date will be [{now_plus_eta}]"

        return [progress_text, average_text, eta_text]


if __name__ == "__main__":
    import misc.greeter_message
    print("You shouldn't be running this file directly, Dandere2x is class based and those are handled by dandere2x.py which is controlled by dandere2x_cli.py or a gui")
