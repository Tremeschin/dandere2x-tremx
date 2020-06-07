"""
===============================================================================

Purpose: Where stuff should be and move to

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

from utils import Utils
import sys
import os


class Directories():
    def __init__(self):
        self.utils = Utils()
        self.config = self.utils.load_yaml(self.utils.ROOT + os.path.sep + "directories.yaml", log=False)

        self.dirs = self.config["directories"]
        self.files = self.config["files"]

        self.session_name = None
        self.input_filename = None
        self.directories = {"dirs": {}, "files": {}}

    def replace_syntax(self, item):
        for replacing in self.replace:
            item = item.replace(replacing[0], replacing[1])
        return item

    # We expect the user to give self.session_name and self.input_filename to Directories before running this
    def generate_dirs(self):

        if self.session_name == None:
            print("Not set session_name on Directories")
            sys.exit(0)

        if self.input_filename == None:
            print("Not set input_filename on Directories")
            sys.exit(0)

        if self.config["tweaks"]["linux"]["release_rootfolder_homepath"]:
            if os.name == "posix":
                # We'll set ROOT to $HOME for the folders and files a session have.
                self.utils.ROOT = self.utils.env_var("HOME") + os.path.sep + ".dandere2x"

        # Double slashes as you can't create a dir with those either on Linux or Windows
        self.replace = [
            ["//ROOT//", self.utils.ROOT],
            ["//SESSION//", self.session_name],
            ["//INPUTVIDEOFILENAME//", self.input_filename],
            ["|", os.path.sep],  # THIS MUST BE THE LAST
        ]

        # The session folder requires //ROOT//, so we generate it and add its replacement first on self.replace list
        self.sesions_folder = self.replace_syntax(self.dirs["sessions_folder"])
        self.replace = [["//SESSIONFOLDER//", self.sesions_folder + os.path.sep + self.session_name]] + self.replace

        for item in self.dirs:
            self.directories["dirs"][item] = self.replace_syntax(self.dirs[item])
        
        for item in self.files:
            self.directories["files"][item] = self.replace_syntax(self.files[item])

        self.plain_dirs = []
        for item in self.directories["dirs"].keys():
            self.plain_dirs.append(self.directories["dirs"][item])

        self.plain_files = []
        for item in self.directories["files"].keys():
            self.plain_files.append(self.directories["files"][item])

        print(self.directories)

    def get(self, item):
        try:
            return self.directories["dirs"][item]
        except KeyError:
            return self.directories["files"][item]
        raise("Directory not found in Directories()")


# Testing
if __name__ == "__main__":
    d = Directories()
    d.session_name = "abc"
    d.input_filename = "yn"
    d.generate_dirs()