"""
===============================================================================

Purpose: Set of utilities for Dandere2x, miscellaneous functions, also logging

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

from inspect import currentframe
from color import colors, fg, bg
import subprocess
import threading
import datetime
import random
import shutil
import yaml
import time
import sys
import os
import re


color = colors["utils"]


class Utils():

    # Init the log file
    def __init__(self):
        self.ROOT = self.get_root()

        # To display on the gui the last status of the session
        self.last_log = ""

    # On where the session name is set to "auto"
    def get_auto_session_name(self, input_file):

        debug_prefix = "[Utils.get_auto_session_name]"

        session_name = os.path.splitext(os.path.basename(input_file))[0]

        self.log(color, 1, debug_prefix, "Session name is AUTO, setting it to: [%s]" % session_name)

        return session_name

    # As utils and context, controller are two separate classes
    def set_context(self, context):
        self.context = context

    # Get Controller
    def set_controller(self, controller):
        self.controller = controller

    # Get this file "absolute" path for relative reference
    def get_root(self):
        return os.path.dirname(os.path.abspath(__file__))

    # Get line number which this function is called, debugging
    def get_linenumber(self):
        return currentframe().f_back.f_lineno

    # Transform eg. zero_padded(23, 5) -> 00023
    def zero_padded(self, number, digits):
        return str(number).zfill(digits)

    # Returns with default value of zero padding total digits
    def pad_zeros(self, number):
        return self.zero_padded(number, self.context.zero_padding)

    # Make directory if it does not exist
    def mkdir_dne(self, directory):

        debug_prefix = "[Utils.mkdir_dne]"

        if not os.path.isdir(directory):
            self.log(color, 2, debug_prefix, "Directory does NOT exist, creating: [%s]" % directory)
            os.makedirs(directory)
        else:
            self.log(color, 2, debug_prefix, "Directory already exists: [%s]" % directory)

    # Reset file (write empty) or create it
    def reset_file(self, filename):

        debug_prefix = "[Utils.reset_file]"

        if os.path.isfile(filename):
            self.log(color, 2, debug_prefix, "File exists, reseting it: [%s]" % filename)
        else:
            self.log(color, 2, debug_prefix, "File does NOT exist, creating empty: [%s]" % filename)

        with open(filename, "w") as f:
            f.write("")

    # Delete the file if it exists
    def delete_file(self, filename):

        debug_prefix = "[Utils.delete_file]"

        # If it even exists
        if os.path.isfile(filename):
            
            self.log(color, 7, debug_prefix, "File exists, deleting it: [%s]" % filename)

            try:
                os.remove(filename)
            except (PermissionError, FileNotFoundError):
                # TODO: handle this better? Windows PermissionErrors?
                self.log(color, 7,  debug_prefix, "PermissionError, FileNotFoundError deleting [%s]" % filename)

        else:
            self.log(color, 7, debug_prefix, "File does NOT exist")

    # /some/dir/file.ext -> "file.ext"
    def get_basename(self, path):

        debug_prefix = "[Utils.get_basename]"

        basename = os.path.basename(path)

        self.log(color, 6   , debug_prefix, "Getting basename of [%s] = [%s]" % (path, basename))

        return basename

    # Returns the path of a auto output file
    def auto_output_file(self, input_file, upscale_ratio, upscaler_type):
        filename = os.path.basename(input_file)
        output_file = input_file.replace(filename, f"{upscale_ratio}x_{upscaler_type}_{filename}")
        return output_file

    # Wrapper for self.mkdir_dne, checks the plain dirs from context
    def check_dirs(self):
        for directory in self.context.plain_dirs:
            self.mkdir_dne(directory)

    # Wrapper for self.reset_file, resets the plain files from context
    def reset_files(self):
        for item in self.context.plain_files:
            # Not healthy to reset partials
            if not "//NUM//" in item:
                self.reset_file(item)

    # Deletes an directory, fail safe? Quits if
    def rmdir(self, directory):

        debug_prefix = "[Utils.rmdir]"

        if os.path.isdir(directory):

            self.log(color, 3, debug_prefix, "Removing dir: [%s]" % directory)

            # Try removing with ignoring errors first..?
            shutil.rmtree(directory, ignore_errors=True)

            # Not deleted?
            if os.path.isdir(directory):
                self.log(color, 3, debug_prefix, "Error removing directory with ignore_errors=True, trying again")

                # Remove without ignoring errors?
                shutil.rmtree(directory, ignore_errors=False)

                # Still exists? oops, better quit
                if os.path.isdir(directory):
                    self.log(colors["error"], 0, debug_prefix, "COULD NOT REMOVE DIRECTORY: [%s]" % directory)
                    sys.exit(-1)

            self.log(color, 4, debug_prefix, "Removed successfully")
        else:
            self.log(color, 3, debug_prefix, "Directory exists, skipping... [%s]" % directory)

    # Debugging, show context static files
    def show_static_files(self):

        debug_prefix = "[Utils.show_static_files]"

        for item in self.context.plain_files:
            self.log(color, 4, debug_prefix, "Static file: [%s]" % item)

    # Get operating system
    def get_os(self):

        debug_prefix = "[Utils.get_os]"

        name = os.name

        self.log(color, 1, debug_prefix, "os.name is [%s]" % name)

        # Not really specific but should work?
        if name == "posix":
            os_name = "linux"

        if name == "nt":
            os_name = "windows"

        self.log(color, 1, debug_prefix, "Got operating system:", os_name)

        return os_name

    # Return OS environment var like XDG_SESSION_TYPE or PATH
    def env_var(self, var):
        return os.environ[var]

    # Simply run a subprocess
    def run_subprocess(self, command):
        subprocess.run(command)

    # Get the output of a command with os module
    def command_output(self, command):
        return os.popen(command).read()

    # Get the output of a command with subprocess module with check_output
    def command_output_subprocess(self, command):
        return subprocess.check_output(command, stderr=subprocess.STDOUT).decode("utf-8")

    # "Pipe" subprocess stdout to python
    def command_output_subprocess_with_stdout(self, command):
        out = subprocess.run(command, capture_output=True).stdout
        return out.decode("utf-8")

    # Wipe out logs.log file and set a self.logfile
    def clean_set_log(self):

        debug_prefix = "[Utils.clean_set_log]"

        # The default position of the logfile, we move it in a bit when we create Context
        self.logfile = self.ROOT + os.path.sep + "logs.log"

        # Delete log file as it exists
        if os.path.isfile(self.logfile):
            print(color + debug_prefix, "Log file exists, deleting it: [%s]" % self.logfile, fg.rs)
            os.remove(self.logfile)
        else:
            print(color, debug_prefix, "Log file does NOT exist", fg.rs)

        with open(self.logfile, "w") as f:
            f.write("")

        self.log(color, 0, debug_prefix, "Reseted log file")

    # Set new path to logfile and move the old one TODO can be problematic?
    def move_log_file(self, new_logfile):

        debug_prefix = "[Utils.move_log_file]"

        self.log(color, 2, debug_prefix, "Moving log file from [%s] to [%s]" % (self.logfile, new_logfile))

        self.rename(self.logfile, new_logfile)

        self.logfile = new_logfile

        self.log(color, 2, debug_prefix, "Setted logfile to [%s]" % new_logfile)

    # Is this overengineered? Joins message into a str
    # TODO: Simplify this?
    def log(self, color, loglevel_required, *message):

        # We do this because generating datetime on every log call might be expensive
        # And we give Utils, Context later on so we'll have to wait to see the actual loglevel
        try:
            if not self.context.loglevel >= loglevel_required:
                return
        except Exception:
            pass
        
        # When was this logged
        now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S,%f")[:-3]

        processed_message = "[%s] " % now

        # Basically we define *message as an argument so we have to
        # "merge" it, ' '.join(everything)
        for index, item in enumerate(message):
            if isinstance(item, list) or isinstance(item, tuple):
                processed_message += " ".join(map(str, message[index])) + " "
            else:
                processed_message += str(item) + " "

        # As we add that extra space at the end, gotta remove it
        processed_message = processed_message[:-1]
        
        print(color + processed_message + fg.rs + bg.rs)

        # Display on the GUI the latest status
        self.last_log = processed_message

        # We give Utils, Context later on so we'll have to wait to see if write_log is T or F
        try:
            if self.context.write_log:
                with open(self.logfile, "a") as f:
                    f.write(processed_message + "\n")
        except Exception:
            with open(self.logfile, "a") as f:
                f.write(processed_message + "\n")

    # Safely load yaml file, just for cleaness of code
    def load_yaml(self, filename, log=True):

        debug_prefix = "[Utils.load_yaml]"

        if log:
            self.log(color, 2, debug_prefix, "Loading YAML file: [%s]" % filename)

        # Open and load the YAML
        with open(filename, "r") as f:
            data = yaml.safe_load(f)

        return data

    # Save data to filename in yaml syntax
    def save_yaml(self, data, filename):

        debug_prefix = "[Utils.save_yaml]"

        self.log(color, 4, debug_prefix, "Saving to YAML file: [%s]" % filename)

        # Open and save to YAML
        with open(filename, "w") as f:
            yaml.dump(data, f)

    # Check if context_vars file exist and returns the "resume" key value
    def check_resume(self):

        debug_prefix = "[Utils.check_resume]"

        self.log(color, 1, debug_prefix, "Checking")

        # Does the context.context_vars file exist?
        if os.path.isfile(self.context.context_vars):

            # Load the data into it
            data = self.load_yaml(self.context.context_vars)

            # Is the key resume present?
            if "resume" in data:

                text = "True" if data["resume"] else "False"
                self.log(color, 1, debug_prefix, "Resume key in session vars: [%s]" % text)

                # Return its real data, is or isn't resume?
                return data["resume"]

            # Does not contain resume keyword, probably blank file?
            self.log(color, 1, debug_prefix, "Resume key not in session vars: [False]")
            return False
        else:
            # No file exist, assuming no previous session
            self.log(color, 1, debug_prefix, "Session vars file does not exist")
            return False

    # Waits until file exist or controller stop var is True
    def until_exist(self, path):

        debug_prefix = "[Utils.until_exist]"

        self.log(color, 6, debug_prefix, "Waiting for file or diretory: [%s]" % path)

        while True:
            # Path exist or controller says stop: break
            if self.controller.stop:
                self.log(color, 4, debug_prefix, "Quitting waiting: [%s]" % path)
                break
            if os.path.exists(path):
                self.log(color, 6, debug_prefix, "Waited done: [%s]" % path)
                break
            
            # Wait or we'll hang this Python GIL thread
            time.sleep(self.context.wait_time)

    # Rename file or directory, basically move it with shutil will be less troublesome
    def rename(self, old, new):

        debug_prefix = "[Utils.rename]"

        self.log(color, 2, debug_prefix, "Moving [%s] --> [%s]" % (old, new))

        shutil.move(old, new)

    # Utility for string.replace(old, new) that substitutes with a dictionary
    def replace_by_dictionary(self, dictionary, replaced):

        # Debug info, show the original string to be replaced and the dictionary
        debug_prefix = "[Utils.replace_by_dictionary]"

        self.log(color, 8, debug_prefix, "Replacing string [\"%s\"] with dictionary:" % replaced)

        for key in list(dictionary.keys()):
            self.log(color, 8, self.context.indentation + debug_prefix, "[\"%s\"] = [\"%s\"]" % (key, dictionary[key]))

        # Actually replace the string we want
        for key in list( dictionary.keys() ):
            replaced = replaced.replace(key, dictionary[key])

        self.log(color, 8, debug_prefix, "Replaced string: [\"%s\"]" % replaced)

        return replaced

    # Get the next partial video path to pipe images
    def get_partial_video_path(self):

        debug_prefix = "[Utils.get_partial_video_path]"

        partial = self.context.partial_video.replace("//NUM//", str(len(os.listdir(self.context.partial))))

        self.log(color, 1, debug_prefix, "Partial video file is: [%s]" % partial)

        return partial

    # For resume sessions, we gotta start with the last image piped to the last video
    def get_last_partial_video_path(self):

        debug_prefix = "[Utils.get_last_partial_video_path]"

        files = os.listdir(self.context.partial)

        self.log(color, 1, debug_prefix, "All partials:", files)

        # Sort the files numerically
        files = [int(x.replace(".mkv", "")) for x in files]
        files.sort()
        last_partial_file = [str(x) + ".mkv" for x in files][-1]

        self.log(color, 1, debug_prefix, "Last partial is: [%s]" % last_partial_file)

        last_partial_path = self.context.partial + last_partial_file

        return last_partial_path

    # get_nth_word("abc def ggf 23894d", 3) -> "ggf"
    def get_nth_word(self, string, N):
        return string.split(' ')[N-1]

    # "asd23asd345" -> 23
    def get_first_number_of_string(self, string):
        return int(re.search(r'\d+', string).group())

    # Search binary in path first then externals for Linux and Windows directly into externals
    def get_binary(self, wanted):

        debug_prefix = "[Utils.get_binary]"

        # Linux way of life
        if self.context.os == "linux":

            command = "whereis " + wanted

            self.log(color, 2, debug_prefix, "Sending command to verify:", command)

            out = self.command_output(command).replace("\n", "")

            self.log(color, 2, debug_prefix, "Got output:", out)

            if not out == wanted + ":":

                # out = "ls: /usr/bin/ls /usr/share/man/man1/ls.1p.gz /usr/share/man/man1/ls.1.gz"
                # out = "asdasd:"

                # Get the first binary pointed by whereis TODO: is this right?
                out = self.get_nth_word(out, 2)

                # This is the binary from where we're going to execute upscaler
                return out

            # Else search in externals as we do with Windows
            else:

                self.log(colors["error"], 2, debug_prefix, "Couldn't find %s binary in PATH, searching in externals, is this right?" % wanted)
                self.log(color, 2, debug_prefix, "Searching [%s] in ./externals/*" % wanted)

                full_path_wanted = None

                # Iterate into externals file tree
                # for root, dirs, files (annoying warning messages and "_" is ignore as we don't use dirs)
                for root, _, files in os.walk(self.context.ROOT + os.path.sep + "externals"):

                    # Exit loop as the file was found as we're inside two loops
                    if not full_path_wanted == None:
                        break

                    # For every file in a folder
                    for f in files:

                        # Hard debug
                        self.log(color, 5, debug_prefix, "[DEBUG] Scanning [%s] == [%s]" % (wanted, f))

                        # If wanted matches some file name we're looping
                        if wanted in f.lower():

                            # Get the full path by joining the root search and the target wanted
                            full_path_wanted = os.path.join(root, wanted)

                            self.log(colors["good"], 1, debug_prefix, "Got executable, full path: [%s]" % full_path_wanted)

                            # Exit "for every file in a folder" loop
                            break

                # Nothing was found, exit
                if full_path_wanted == None:
                    self.log(color, 0, debug_prefix, "[ERROR]: Binary [%s] not found in [\"%s\"]" % (wanted, wanted))
                    return None

                # This will yield false on Linux if forcing windows mode for debugging
                # because Windows is case insensitive and Linux case sensitive
                if os.path.exists(full_path_wanted):
                    self.log(color, 2, debug_prefix, "Binary [%s] exists and is: [\"%s\"]" % (wanted, full_path_wanted))
                    return full_path_wanted

        # Search for "ROOT/externals/$wanted$.exe"
        elif self.context.os == "windows":

            # As our searches should be OS independent we only "ask" for the file name
            executable = wanted + ".exe"

            self.log(color, 2, debug_prefix, "Searching [%s] in ./externals/*" % executable)

            full_path_executable = None

            # Iterate into externals file tree
            # for root, dirs, files (annoying warning messages and "_" is ignore as we don't use dirs)
            for root, _, files in os.walk(self.context.ROOT + os.path.sep + "externals"):

                # Exit loop as the file was found as we're inside two loops
                if not full_path_executable == None:
                    break

                # For every file in a folder
                for f in files:

                    # Hard debug
                    self.log(color, 5, debug_prefix, "[DEBUG] Scanning [%s] == [%s]" % (executable, f))

                    # If executable matches some file name we're looping
                    if executable in f.lower():

                        # Get the full path by joining the root search and the target executable
                        full_path_executable = os.path.join(root, executable)

                        full_path_executable = os.path.abspath(full_path_executable)

                        self.log(colors["good"], 2, debug_prefix, "Got executable, full path: [%s]" % full_path_executable)

                        # Exit "for every file in a folder" loop
                        break

            # Nothing was found, exit
            if full_path_executable == None:
                self.log(color, 0, debug_prefix, "[ERROR]: Binary [%s] not found in [\"%s\"]" % (wanted, executable))
                exit()

            # This will yield false on Linux if forcing windows mode for debugging
            # because Windows is case insensitive and Linux case sensitive
            if os.path.exists(full_path_executable):
                self.log(color, 2, debug_prefix, "Binary [%s] exists and is: [\"%s\"]" % (executable, full_path_executable))
                return full_path_executable


# Python's subprocess wrapper to make things easier, should be its own file
# but it's not that large and it's technically a utility, so...
class SubprocessUtils():

    def __init__(self, name, utils, context):

        debug_prefix = "[SubprocessUtils.__init__]"

        self.name = name
        self.utils = utils
        self.context = context

        self.utils.log(color, 5, debug_prefix, "Creating SubprocessUtils with name: [%s]" % name)

    # Get the commands from a list to call the subprocess
    def from_list(self, list):

        debug_prefix = "[SubprocessUtils.run]"

        self.utils.log(color, 5, debug_prefix, "Getting command from list:")
        self.utils.log(color, 5, debug_prefix, list)

        self.command = list

    # Run the subprocess with or without a env / working directory
    def run(self, working_directory=None, env=None):

        debug_prefix = "[SubprocessUtils.run]"
        
        self.utils.log(color, 5, debug_prefix, "Popen SubprocessUtils with name [%s]" % self.name)
        
        # Copy the environment if nothing was changed and passed as argument
        if env is None:
            env = os.environ.copy()

        # Yes, shell=True is not at all recommended but in my tests on Windows it was kinda necessary?
        if self.context.os == "windows":
            shell = True
        else:
            shell = False
        
        # Runs the subprocess based on if we set or not a working_directory
        if working_directory == None:
            self.process = subprocess.Popen(self.command, env=env, stdout=subprocess.PIPE, shell=shell)
        else:
            self.process = subprocess.Popen(self.command, env=env, cwd=working_directory, stdout=subprocess.PIPE, shell=shell)

    # Get the newlines from the subprocess
    # This is used for communicating Dandere2x C++ with Python, simplifies having dealing with files
    def realtime_output(self):
        while True:
            # Read next line
            output = self.process.stdout.readline()

            # If output is empty and process is not alive, quit
            if output == '' and self.process.poll() is not None:
                break
            
            # Else yield the decoded output as subprocess send bytes
            if output:
                yield output.strip().decode("utf-8")

    # Wait until the subprocess has finished
    def wait(self):

        debug_prefix = "[SubprocessUtils.wait]"

        self.utils.log(color, 4, debug_prefix, "Waiting SubprocessUtils with name [%s] to finish" % self.name)

        self.process.wait()

    # Kill subprocess
    def terminate(self):

        debug_prefix = "[SubprocessUtils.terminate]"

        self.utils.log(color, 4, debug_prefix, "Terminating SubprocessUtils with name [%s]" % self.name)

        self.process.terminate()

    # See if subprocess is still running
    def is_alive(self):

        debug_prefix = "[SubprocessUtils.is_alive]"

        # Get the status of the subprocess
        status = self.process.poll()

        # None? alive
        if status == None:
            return True
        else:
            self.utils.log(color, 3, debug_prefix, " SubprocessUtils with name [%s] is not alive" % self.name)
            return False


if __name__ == "__main__":
    import misc.greeter_message
    print("You shouldn't be running this file directly, Dandere2x is class based and those are handled by dandere2x.py which is controlled by dandere2x_cli.py or a gui")
