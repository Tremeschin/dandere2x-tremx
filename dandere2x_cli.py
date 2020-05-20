from dandere2x import Dandere2x
from utils import Utils

import argparse
import os


if __name__ == "__main__":

    utils = Utils()

    print("NOTE: Not a single argument is required, will load the settings.yaml configurations and overwrite them with the user provided ones")

    # Create ArgumentParser
    args = argparse.ArgumentParser(description='Arguments for Dandere2x CLI')

    # # Arguments

    # Force deletion of session, don't resume
    args.add_argument('-f', '--force', required=False, action="store_true", help="(solo) Forces resume=False, yielding deletion of session (restart)")

    args.add_argument("-i", "--input", required=False, help="(string) Input path of the video file to be upscaled")
    args.add_argument("-o", "--output", required=False, help="(string) Output path of the upscaled video | NOTE: Can be \"auto\", appends \"2x_\" at the filename of the input video")

    args.add_argument("-w", "--waifu2x", required=False, help="(string) What Waifu2x vertion to use: [fake, vulkan, cpp, caffe]")

    args.add_argument("-b", "--block_size", required=False, help="(int) Block size Dandere2x will work with")
    args.add_argument("-n", "--denoise_level", required=False, help="(int [0, 3]) How much denoise Waifu2x will apply")
    args.add_argument("-t", "--tile_size", required=False, help="(int) Tile size Waifu2x will use")

    args.add_argument("-d", "--debug_video", required=False, action="store_true", help="(solo) Only generate the debug video, WILL NOT UPSCALE")



    # Parse args and make dictionary
    args = args.parse_args()

    args = {
        "force": args.force,
        "input": args.input,
        "output": args.output,
        "waifu2x": args.waifu2x,
        "block_size": args.block_size,
        "denoise_level": args.denoise_level,
        "tile_size": args.tile_size,
        "debug_video": args.debug_video
    }

    user_modified = []

    # Build the config based on arguments

    config = utils.load_yaml(utils.ROOT + os.path.sep + "settings.yaml", log=False)

    if args["force"]:
        user_modified.append("force=True")
        config["danger_zone"]["force"] = True

    if not args["input"] == None:
        user_modified.append("input_file=\"%s\"" % args["input"])
        config["basic"]["input_file"] = args["input"]

    if not args["output"] == None:
        user_modified.append("output_file=\"%s\"" % args["output"])
        config["basic"]["output_file"] = args["output"]

    if not args["waifu2x"] == None:
        user_modified.append("waifu2x=\"%s\"" % args["waifu2x"])
        config["waifu2x_type"] = args["waifu2x"]

    if not args["block_size"] == None:
        user_modified.append("block_size=\"%s\"" % args["block_size"])
        config["processing"]["block_size"] = args["block_size"]

    if not args["denoise_level"] == None:
        user_modified.append("denoise_level=\"%s\"" % args["denoise_level"])
        config["waifu2x"]["denoise_level"] = args["denoise_level"]

    if not args["tile_size"] == None:
        user_modified.append("tile_size=\"%s\"" % args["tile_size"])
        config["waifu2x"]["tile_size"] = args["tile_size"]

    if not args["debug_video"] == False:
        user_modified.append("debug_video=\"%s\"" % args["debug_video"])
        config["debug"]["write_only_debug_video"] = args["debug_video"]

    print(args)

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
