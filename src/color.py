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

# Windows PowerShell we gotta init the colors
import colorama; colorama.init()

def rgb(r, g, b):
    return fg(r, g, b)

# Dictionary that controls the colors of the Dandere2x files
colors = {
    # global
    "error": fg.li_red,
    "hard_warning": fg.li_yellow,
    "warning": fg.yellow,
    "debug": fg.yellow,
    "good": fg.li_green,

    # basic
    "white": fg.li_white,
    "blue": fg.li_blue,
    "li_magenta": fg.li_magenta,
    "li_red": fg.li_red,

    # files
    "dandere2x": fg.li_cyan,  # dandere2x.py
    "phases": fg.li_yellow,  # dandere2x.py
    "utils": fg.li_blue,  # utils.py
    "controller": fg.green,  # controller.py
    "context": fg.li_yellow,  # context.py   
    "processing": fg.li_cyan,  # processing.py
    "frame": fg.li_white,  # frame.py
    "core": fg.cyan,  # core.py
    "stats": fg.li_white,  # stats.py
    "d2xcpp": fg.white,  # d2xcpp.py
    "video": fg.green,  # video.py
    "upscaler": fg.li_cyan,  # waifu2x.py
    "vp": fg.li_white  # vp.py 
}

if __name__ == "__main__":
    from utils import Miscellaneous
    print("You shouldn't be running this file directly, Dandere2x is class based and those are handled by dandere2x.py which is controlled by dandere2x_cli.py or a gui")
