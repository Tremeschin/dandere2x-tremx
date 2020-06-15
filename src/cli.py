"""
===============================================================================

Purpose: CLI interface for Dandere2x

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

from dandere2x import Dandere2x
from utils import Miscellaneous
from utils import Utils

import argparse
import os


if __name__ == "__main__":

    Miscellaneous()
    utils = Utils()

    # Create ArgumentParser
    args = argparse.ArgumentParser(description='Arguments for Dandere2x CLI, NOTE: Not a single argument is required, will load the settings.yaml configurations and overwrite them with the user provided ones. Not all arguments apply to every upscaler, see each one repo for more info.')

    # # Arguments

    # Force deletion of session, don't resume
    args.add_argument('-f', '--force', required=False, action="store_true", help="(solo) Forces resume=False, yielding deletion of session (restart)")

    args.add_argument("-i", "--input", required=False, help="(string) Input path of the video file to be upscaled")
    args.add_argument("-o", "--output", required=False, help="(string) Output path of the upscaled video | NOTE: Can be \"auto\", appends \"2x_\" at the filename of the input video")

    args.add_argument("-u", "--upscaler", required=False, help="(string) What upscaler vertion to use: [fake, vulkan, cpp, caffe]")

    args.add_argument("-b", "--block_size", required=False, help="(int) Block size Dandere2x will work with")
    args.add_argument("-n", "--denoise_level", required=False, help="(int [0, 3]) How much denoise upscaler will apply")
    args.add_argument("-t", "--tile_size", required=False, help="(int) Tile size upscaler will use")

    args.add_argument("-d", "--debug_video", required=False, action="store_true", help="(solo) Only generate the debug video, WILL NOT UPSCALE")

    args.add_argument("-p", "--profile", required=False, help="(string) Load this config file under /dandere2x/profiles/$name$.yaml, defaults to \"user\"")


    # Parse args and make dictionary
    args = args.parse_args()

    args = {
        "force": args.force,
        "input": args.input,
        "output": args.output,
        "upscaler": args.upscaler,
        "block_size": args.block_size,
        "denoise_level": args.denoise_level,
        "tile_size": args.tile_size,
        "debug_video": args.debug_video,
        "profile": args.profile
    }

    user_modified = []

    # Build the config based on arguments

    config_file = args["profile"]

    if args["profile"] == None:
        config_file = utils.ROOT + os.path.sep + "profiles" + os.path.sep + "user.yaml"
    else:
        
        if not ".yaml" in config_file:
            config_file += ".yaml"

        # If the user did not sent us a absolute path
        if not os.path.isabs(config_file):
            config_file = utils.ROOT + os.path.sep + "profiles" + os.path.sep + config_file

    print("Loading Dandere2x with config file: [%s]" % config_file)

    config = utils.load_yaml(config_file, log=False)

    if args["force"]:
        user_modified.append("force=True")
        config["danger_zone"]["force"] = True

    if not args["input"] == None:
        user_modified.append("input_file=\"%s\"" % args["input"])
        config["basic"]["input_file"] = args["input"]

    if not args["output"] == None:
        user_modified.append("output_file=\"%s\"" % args["output"])
        config["basic"]["output_file"] = args["output"]

    if not args["upscaler"] == None:
        user_modified.append("upscaler=\"%s\"" % args["upscaler"])
        config["upscaler"]["type"] = args["upscaler"]

    if not args["block_size"] == None:
        user_modified.append("block_size=\"%s\"" % args["block_size"])
        config["block_matching"]["block_size"] = args["block_size"]

    if not args["denoise_level"] == None:
        user_modified.append("denoise_level=\"%s\"" % args["denoise_level"])
        config["upscaler"]["denoise_level"] = args["denoise_level"]

    if not args["tile_size"] == None:
        user_modified.append("tile_size=\"%s\"" % args["tile_size"])
        config["upscaler"]["tile_size"] = args["tile_size"]

    if not args["debug_video"] == False:
        user_modified.append("debug_video=\"%s\"" % args["debug_video"])
        config["debug"]["write_debug_video"] = args["debug_video"]

    print("[DEBUG] ENTERED ARGS, PLEASE CHECK: ", args)

    # Run Dandere2x
    d2x = Dandere2x(config)
    d2x.load()
    d2x.setup()

    try:
        d2x.run()
    except KeyboardInterrupt:
        print("KeyboardInterrupt catched, saving and exiting..")
        d2x.controller.exit()
        d2x.context.resume = True
        d2x.context.save_vars()
