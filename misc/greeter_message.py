# Print this awesome greeting message

import os

ROOT = os.path.dirname(os.path.abspath(__file__))

with open(ROOT + os.path.sep + "version.txt", "r") as f:
    version = f.read()

message = f"""
----------------------------------------------------
   _____                  _               ___       
  |  __ \\                | |             |__ \\      
  | |  | | __ _ _ __   __| | ___ _ __ ___   ) |_  __
  | |  | |/ _` | '_ \\ / _` |/ _ \\ '__/ _ \\ / /\\ \\/ /
  | |__| | (_| | | | | (_| |  __/ | |  __// /_ >  < 
  |_____/ \\__,_|_| |_|\\__,_|\\___|_|  \\___|____/_/\\_\\

               Fast video upscaling
{(51-len("Version")-len(version))*" "}Version {version}
----------------------------------------------------
Tremx version, made with ❤︎
----------------------------------------------------
"""

# That expression makes sure the end of that line matches the end of the ASCII art :)

print(message)