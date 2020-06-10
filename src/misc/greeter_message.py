# Print this awesome greeting message

import shutil
import math
import os

terminal_width = shutil.get_terminal_size()[0]

ROOT = os.path.dirname(os.path.abspath(__file__))

with open(ROOT + os.path.sep + "version.txt", "r", encoding="utf-8") as f:
    version = f.read()

bias = " "*(math.floor(terminal_width/2) - 25)

message = f"""
{"-"*terminal_width}
{bias} _____                  _               ___       
{bias}|  __ \\                | |             |__ \\      
{bias}| |  | | __ _ _ __   __| | ___ _ __ ___   ) |_  __
{bias}| |  | |/ _` | '_ \\ / _` |/ _ \\ '__/ _ \\ / /\\ \\/ /
{bias}| |__| | (_| | | | | (_| |  __/ | |  __// /_ >  < 
{bias}|_____/ \\__,_|_| |_|\\__,_|\\___|_|  \\___|____/_/\\_\\

{bias}               Fast video upscaling
{bias}{(49-len("Version")-len(version))*" "}Version {version}
{"-"*terminal_width}
 > Tremx version, made with <3
{"-"*terminal_width}
"""

# That expression makes sure the end of that line matches the end of the ASCII art :)

print(message)