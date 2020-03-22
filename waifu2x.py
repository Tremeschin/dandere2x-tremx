# waifu2x wrappers

from color import *


color = rgb(255, 200, 10)


class Waifu2x():
    def __init__(self, context, utils):
        self.context = context
        self.utils = utils
        self.waifu2x = None

    # Set internal self.waifu2x to a specific wrapper based on the os and w2x selected
    def set_corresponding_verify(self):

        debug_prefix = "[Waifu2x.set_corresponding_verify]"
        identation = "  >"
        c = fg.li_magenta # Print this color only in this class

        self.utils.log(c, debug_prefix, "According to the following, ...")

        self.utils.log(c, identation, "OS: " + self.context.os)
        self.utils.log(c, identation, "Waifu2x: " + self.context.waifu2x_type)

        # Set waifu2x based on the OS and type selected
        if self.context.os == "linux":
            
            if self.context.waifu2x_type == "vulkan":
                self.waifu2x = Waifu2xLinuxVulkan(self.context, self.utils)

            if self.context.waifu2x_type == "cpp":
                self.waifu2x = Waifu2xLinuxCPP(self.context, self.utils)

        # Windows os, so Windows Waifu2x wrapper classes
        elif self.context.os == "windows":
            if self.context.waifu2x_type == "vulkan":
                self.waifu2x = Waifu2xWindowsVulkan(self.context, self.utils)

            if self.context.waifu2x_type == "cpp":
                self.waifu2x = Waifu2xWindowsVulkan(self.context, self.utils)

        
        self.waifu2x.verify()






# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Linux


# # For verifying waifu2x binary is in path:

# bash: type: waifu2x-ncnn-vulkan is /usr/bin/waifu2x-ncnn-vulkan
# bash: type: waifu2x-ncnn-vulka: not found
# [TODO]: This only finds waifu2x's in PATH]


# # GetBinary just parses the output and returns the binary of the waifu2x

def LinuxVerify_GetBinary(utils, waifu2x):

    debug_prefix = "[waifu2x.py.LinuxVerify_GetBinary]"

    # Get output of the command
    
    command = "type " + waifu2x
    c = fg.li_blue

    utils.log(c, debug_prefix, "Sending command to verify:", command)
    out = utils.command_output(command).replace("\n", "")
    utils.log(c, debug_prefix, "Got output:", out)

    if "not found" in out:
        utils.log(fg.red, debug_prefix, "Couldn't find %s Waifu2x in PATH" % waifu2x)
        utils.exit()
    

    # out = "bash: type: waifu2x-ncnn-vulkan is /usr/bin/waifu2x-ncnn-vulkan"

    # Get the last portion of text after " is "
    out = out.split(" is ")[-1] 

    # This is the binary from where we're going to execute waifu2x
    return out


# Waifu2x Linux Vulkan (ncnn) wrapper
class Waifu2xLinuxVulkan():

    def __init__(self, context, utils):
        self.context = context
        self.utils = utils

        debug_prefix = "[Waifu2xLinuxVulkan.__init__]"

        self.utils.log(color, debug_prefix, "Will use this Waifu2x wrapper")


    def verify(self):

        debug_prefix = "[Waifu2xLinuxVulkan.verify]"

        self.utils.log(color, debug_prefix, "Verifying and getting binary")

        self.binary = LinuxVerify_GetBinary(self.utils, "waifu2x-ncnn-vulkan")

        self.utils.log(color, debug_prefix, "Got binary: [%s]" % self.binary)


# Waifu2x Linux CPP (converter-cp) wrapper
class Waifu2xLinuxCPP():
    
    def __init__(self, context, utils):
        self.context = context
        self.utils = utils

        debug_prefix = "[Waifu2xLinuxCPP.__init__]"

        self.utils.log(color, debug_prefix, "Will use this Waifu2x wrapper")


    def verify(self):

        debug_prefix = "[Waifu2xLinuxCPP.verify]"

        self.utils.log(color, debug_prefix, "Verifying and getting binary")

        self.binary = LinuxVerify_GetBinary(self.utils, "waifu2x-converter-cpp")

        self.utils.log(color, debug_prefix, "Got binary: [%s]" % self.binary)






# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Windows


# Waifu2x Windows Vulkan (ncnn) wrapper
class Waifu2xWindowsVulkan():
    def __init__(self, context, utils):
        self.context = context
        self.utils = utils

        debug_prefix = "[Waifu2xWindowsVulkan.__init__]"

        self.utils.log(color, debug_prefix, "Will use this Waifu2x wrapper")


# Waifu2x Windows CPP (converter-cpp) wrapper
class Waifu2xWindowsCPP():
    def __init__(self, context, utils):
        self.context = context
        self.utils = utils

        debug_prefix = "[Waifu2xWindowsCPP.__init__]"

        self.utils.log(color, debug_prefix, "Will use this Waifu2x wrapper")


# Waifu2x Windows Caffe wrapper
class Waifu2xWindowsCaffe():
    def __init__(self, context, utils):
        self.context = context
        self.utils = utils

        debug_prefix = "[Waifu2xWindowsCaffe.__init__]"

        self.utils.log(color, debug_prefix, "Will use this Waifu2x wrapper")

