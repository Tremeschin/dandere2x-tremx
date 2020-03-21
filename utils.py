# Utils is a file with mostly helpers and utilities hence its name

from sty import fg, bg, ef, rs

import threading
import yaml
import time
import os


color = fg.li_blue


class Utils():

    def __init__(self):
        self.ROOT = self.get_root()
        self.clean_set_log()


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


    # Wrapper for self.mkdir_dne, checks the plain dirs from context
    def check_dirs(self):
        for directory in self.context.plain_dirs:
            self.mkdir_dne(directory)


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


    # As we gotta close the file for exiting and potentially save session here?
    def exit(self):
        self.logfile.close()
        exit(-1)


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
    def updating_file(filename):
        ufile = open(filename, "r")
        ufile.seek(0,2)
        while True:
            line = ufile.readline()
            if not line:
                time.sleep(0.1)
                continue
            yield line

            