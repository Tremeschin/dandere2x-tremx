from sty import fg, bg, ef, rs

import yaml
import os


color = fg.li_blue


class Utils():

    def __init__(self):
        self.ROOT = self.get_root()
        self.clean_set_log()

    def set_context(self, context):
        self.context = context


    def get_root(self):
        return os.path.dirname(os.path.abspath(__file__))
    

    # Make directory if it does not exist
    def mkdir_dne(self, directory):

        debug_prefix = "[Utils.mkdir_dne]"

        if not os.path.isdir(directory):
            self.log(color, debug_prefix, "Directory does NOT exist, creating: %s" % directory)
            os.makedirs(directory)
        else:
            self.log(color, debug_prefix, "Directory already exists: %s" % directory)


    # Wrapper for self.mkdir_dne, checks the plain dirs from context
    def check_dirs(self):
        for directory in self.context.plain_dirs:
            self.mkdir_dne(directory)


    # Get operating system
    def get_os(self):

        debug_prefix = "[Utils.get_os]"

        # Not really specific but should work?
        if os.name == "posix":
            os_name = "linux"
        else:
            os_name = False

        if not os_name == False:
            self.log(color, debug_prefix, "Got operating system:", os_name)
            return os_name

        else:
            self.log(fg.li_red + debug_prefix, "[ERROR] Os not supported:", os_name)
            exit(-1)


    # Return OS environment var like XDG_SESSION_TYPE or PATH
    def env_var(self, var):
        return os.environ[var]
        

    # Wipe out logs.log file and set a self.logfile
    def clean_set_log(self):

        debug_prefix = "[Utils.clean_set_log]"

        with open(self.ROOT + os.path.sep + "logs.log", "w") as f:
            f.write("")

        self.logfile = open("logs.log", "a")

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

        # As we add that extra space at the end
        processed_message = processed_message[:-1]

        print (color + processed_message + fg.rs)
        self.logfile.write(processed_message + "\n")


    def load_yaml(self, filename):
        with open(filename, "r") as f:
            data = yaml.safe_load(f)
        return data

            