"""
===============================================================================

Purpose: Colors, colors, colors!! I'm considering a blue / black background
ie, PowerShell and default black background

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

from sty import fg, bg, ef, rs


def rgb(r, g, b):
    return fg(r, g, b)

# Dictionary that controls the colors of the Dandere2x files
colors = {
    # global
    "error": rgb(255, 0, 0),
    "hard_warning": rgb(255,100,0),
    "warning": fg.li_red,
    "debug": rgb(0, 255, 247),
    "good": rgb(0, 255, 0),

    # basic
    "white": rgb(255, 255, 255),
    "blue": rgb(0, 0, 255),
    "li_magenta": fg.li_magenta,
    "li_red": fg.li_red,

    # files
    "dandere2x": rgb(200, 255, 80),  # dandere2x.py
    "phases": rgb(84, 255, 87),  # dandere2x.py
    "utils": fg.li_blue,  # utils.py
    "controller": rgb(240, 100, 64),  # controller.py
    "context": fg.li_yellow,  # context.py   
    "processing": rgb(0, 255, 0),  # processing.py
    "frame": rgb(196, 255, 33),  # frame.py
    "core": rgb(0, 115, 255),  # core.py
    "stats": rgb(50, 80, 255),  # stats.py
    "d2xcpp": rgb(240, 100, 64),  # d2xcpp.py
    "video": rgb(30, 200, 60),  # video.py
    "upscaler": rgb(255, 200, 10),  # waifu2x.py
    "vp": rgb(120, 230, 200)  # vp.py 
}

if __name__ == "__main__":
    print("You shouldn't be running this file directly, Dandere2x is class based and those are handled by dandere2x.py which is controlled by dandere2x_cli.py or the upcoming GUI")
