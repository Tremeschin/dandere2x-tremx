# Utils is a file with mostly helpers and utilities hence its name

from color import *

import threading
import shutil
import yaml
import time
import os


color = color_by_name("li_blue")


class Utils():

    def __init__(self):
        self.ROOT = self.get_root()
        self.clean_set_log()


    # As we gotta close the file for exiting and potentially save session here?
    def exit(self):
        self.logfile.close()
        self.context.stop = True
        exit()


    # As utils and context are two separate classes
    def set_context(self, context):
        self.context = context


    # Get this file "absolute" path for relative reference
    def get_root(self):
        return os.path.dirname(os.path.abspath(__file__))
    

    # Make directory if it does not exist
    def mkdir_dne(self, directory):

        debug_prefix = "[Utils.mkdir_dne]"

        if not os.path.isdir(directory):
            self.log(color, debug_prefix, "Directory does NOT exist, creating: [%s]" % directory)
            os.makedirs(directory)
        else:
            self.log(color, debug_prefix, "Directory already exists: [%s]" % directory)


    # Reset file (write empty) or create it
    def reset_file(self, filename):
        
        debug_prefix = "[Utils.reset_file]"

        if os.path.isfile(filename):
            self.log(color, debug_prefix, "File exists, reseting it: [%s]" % filename)
        else:
            self.log(color, debug_prefix, "File does NOT exist, creating empty: [%s]" % filename)
        
        with open(filename, "w") as f:
                f.write("")


    # Wrapper for self.mkdir_dne, checks the plain dirs from context
    def check_dirs(self):
        for directory in self.context.plain_dirs:
            self.mkdir_dne(directory)


    # Wrapper for self.reset_file, resets the plain files from context
    def reset_files(self):
        for item in self.context.plain_files:
            self.reset_file(item)

    
    # Deletes an directory, fail safe? Quits if 
    def reset_dir(self, directory):
        
        debug_prefix = "[Utils.reset_dir]"

        self.log(color, debug_prefix, "Removing dir: [%s]" % directory)

        shutil.rmtree(directory, ignore_errors=True)

        if os.path.isdir(directory):
            self.log(color, debug_prefix, "Error removing directory with ignore_errors=True, trying again")
            
            shutil.rmtree(directory, ignore_errors=False)

            if os.path.isdir(directory):
                self.log(fg.li_red, debug_prefix, "COULD NOT REMOVE DIRECTORY: [%s]" % directory)
                self.exit()
        
        self.log(color, debug_prefix, "Removed successfully")


    # Debugging, show context static files
    def show_static_files(self):

        debug_prefix = "[Utils.show_static_files]"

        for item in self.context.plain_files:
            self.log(color, debug_prefix, "Static file: [%s]" % item)


    # Get operating system
    def get_os(self):

        debug_prefix = "[Utils.get_os]"

        # Not really specific but should work?
        if os.name == "posix":
            os_name = "linux"

        self.log(color, debug_prefix, "Got operating system:", os_name)
        return os_name


    # Return OS environment var like XDG_SESSION_TYPE or PATH
    def env_var(self, var):
        return os.environ[var]


    # Get the output of a commnd
    def command_output(self, command):
        return os.popen(command).read()
        

    # Wipe out logs.log file and set a self.logfile
    def clean_set_log(self):

        debug_prefix = "[Utils.clean_set_log]"

        logfile = "logs.log"

        with open(self.ROOT + os.path.sep + logfile, "w") as f:
            f.write("")

        self.logfile = open(logfile, "a")

        self.log(color, debug_prefix, "Reseted log file")


    def log(self, color, *message):

        processed_message = ""
        
        # Basically we define *message as an argument so we have to
        # "merge" it, ' '.join(everything)
        for index, item in enumerate(message):
            if isinstance(item, list) or isinstance(item, tuple):
                processed_message += " ".join(message[index]) + " "
            else:
                processed_message += str(item) + " "

        # As we add that extra space at the end, gotta remove it
        processed_message = processed_message[:-1]

        print (color + processed_message + fg.rs)
        self.logfile.write(processed_message + "\n")


    # Safely load yaml file, just for cleaness of code
    def load_yaml(self, filename):

        debug_prefix = "[Utils.load_yaml]"

        self.log(color, debug_prefix, "Loading YAML file: [%s]" % filename)

        with open(filename, "r") as f:
            data = yaml.safe_load(f)
        return data


    # Save data to filename in yaml syntax
    def save_yaml(self, data, filename):

        debug_prefix = "[Utils.save_yaml]"

        self.log(color, debug_prefix, "Saving to YAML file: [%s]" % filename)

        with open(filename, "w") as f:
            yaml.dump(data, f)


    # This "follows" updating files, yields the new stuff written
    def updating_file(self, filename):
        ufile = open(filename, "r")
        ufile.seek(0,2)
        while True:
            line = ufile.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line

            