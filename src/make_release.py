"""
===============================================================================

Purpose: Never spend 5 minutes doing something by hand when you can fail
automating it in 5 hours

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

import sys
sys.path.append('../')

from utils import Miscellaneous
from utils import Utils
import urllib.request
import argparse
import os


# Where we'll work with Wine to make a Windows release
WINEPREFIX = "~/wine/d2x"
WINEPREFIX = WINEPREFIX.replace("~", os.environ["HOME"])
print("WINEPREFIX IS [%s] IF WINDOWS RELEASE" % WINEPREFIX)


class ReleaseMaker():    
    def __init__(self, args):
        self.args = args
        self.utils = Utils()
        self.ROOT = self.utils.ROOT

        self.version = Miscellaneous().version
    
    def run(self):
        if self.args["opencv"]:
            self.opencv_mingw()
        if self.args["windows"]:
            self.windows()

    def runscript(self, name):
        os.system("sh \"%s\"" % self.ROOT + os.path.sep + "release" + os.path.sep + name)

    def opencv_mingw(self):
        self.runscript("build_opencv_mingw.sh")

    def copy_common_files(self):

        d = self.ROOT
        for f in os.listdir(d):
            if f in ["directories.yaml"]:
                self.utils.bash_copy(
                    d + os.path.sep + f,
                    self.release_dir + f
                )
        
        d = self.ROOT + os.path.sep + "profiles"
        for f in os.listdir(d):
            if f.endswith(".yaml"):
                self.utils.bash_copy(
                    d + os.path.sep + f,
                    self.release_dir + "profiles" + os.path.sep + f
                )

        d = self.ROOT + os.path.sep + "samples"
        for f in os.listdir(d):
            if f in ["yn_moving_480.mkv", "yn_moving.mkv"] or f == "legal":
                self.utils.bash_copy(
                    d + os.path.sep + f,
                    self.release_dir + "samples" + os.path.sep + f
                )

        self.utils.bash_copy(
            self.ROOT + os.path.sep + "data" + os.path.sep + "dandere2x-qt-gui.ui",
            self.release_dir + "data" + os.path.sep + "dandere2x-qt-gui.ui"
        )
    
    # Create the dirs needed for a release
    def make_release_dirs(self):
        self.utils.mkdir_dne(self.release_dir)
        for directory in ["externals", "data", "samples", "profiles", "externals" + os.path.sep + "dandere2x_cpp"]:
            self.utils.mkdir_dne(self.release_dir + directory)

    # Make a Windows release
    def windows(self):

        print("MAKE SURE YOU HAVE PYTHON INSTALLED IN THE WINEPREFIX GLOBAL VARIABLE IN THIS FILE")

        self.release_dir = self.ROOT + os.path.sep + "release" + os.path.sep + "releases" + os.path.sep + "windows" + os.path.sep + self.version + os.path.sep
        print("Release directory is:", self.release_dir)

        self.make_release_dirs()

        # Cross compile Dandere2x C++
        
        print("Cross compiling Dandere2x C++ with MinGW")
        self.runscript("crosscompile_d2xcpp_windows.sh")

        self.utils.bash_move(
            self.ROOT + os.path.sep + "externals" + os.path.sep + "dandere2x_cpp.exe",
            self.release_dir + "externals" + os.path.sep + "dandere2x_cpp" + os.path.sep + "dandere2x_cpp.exe"
        )

        # Required DLLs for C++ to work
        d = self.ROOT + os.path.sep + "externals"
        for f in os.listdir(d):
            if "opencv" in f:
                self.utils.bash_move(
                    d + os.path.sep + f,
                    self.release_dir + "externals" + os.path.sep + "dandere2x_cpp" + os.path.sep + f
                )
            
        d = self.ROOT + os.path.sep + "release" + os.path.sep + "thedlls"
        for f in os.listdir(d):
            if f.endswith(".dll"):
                self.utils.bash_copy(
                    d + os.path.sep + f,
                    self.release_dir + "externals" + os.path.sep + "dandere2x_cpp" + os.path.sep + f
                )

        self.copy_common_files()

        # # Done copying the needed files

        # Make a pyinstaller executable

        os.chdir(self.utils.ROOT)

        # # Install required Python modules on the WINEPREFIX and Visual C++

        # Create the WINEPREFIX if it doesn't exist
        os.system("WINEPREFIX=\"%s\" WINEDEBUG=-all wine wineboot" % WINEPREFIX)

        # # Install Python

        save_python = self.ROOT + os.path.sep + "python-3.8.3-amd64.exe"

        # Download python 3.8 64 bit
        print("DOWNLOADING PYTHON")
        urllib.request.urlretrieve("https://www.python.org/ftp/python/3.8.3/python-3.8.3-amd64.exe", save_python)

        # Install our downloaded python in quiet mode and append to the Wine path
        print("INSTALLING PYTHON QUIET, UNATTENDED")
        os.system("WINEPREFIX=\"%s\" WINEDEBUG=-all wine \"%s\" /quiet InstallAllUsers=1 PrependPath=1" % (WINEPREFIX, save_python))

        # Upgrade pip if there is an available version
        os.system("WINEPREFIX=\"%s\" WINEDEBUG=-all wine python -m pip install --upgrade pip" % WINEPREFIX)

        # Install Dandere2x requirements
        os.system("WINEPREFIX=\"%s\" WINEDEBUG=-all wine pip install -r requirements.txt" % WINEPREFIX)

        # Install pyinstaller and pywin32
        os.system("WINEPREFIX=\"%s\" WINEDEBUG=-all wine pip install pyinstaller pywin32" % WINEPREFIX)

        # Install Visual C++ (looks like it's needed by pyinstaller)
        os.system("WINEPREFIX=\"%s\" winetricks --unattended vcrun2015" % WINEPREFIX)

        # The files we want to compile and put on our release
        release_files = ["cli.py", "gui-qt.py", "get_externals.py"]

        for f in release_files:
            binary = f.replace(".py", ".exe")
            
            os.system("WINEPREFIX=\"%s\" WINEDEBUG=-all wine pyinstaller --onefile \"%s\"" % (WINEPREFIX, self.utils.ROOT + os.path.sep + f))
            
            self.utils.bash_move(
                self.utils.ROOT + os.path.sep + "dist" + os.path.sep + binary,
                self.release_dir + binary
            )


if __name__ == "__main__":

    if os.name == "nt":
        print("Making releases using Windows not implemented")

    args = argparse.ArgumentParser(description="Release maker utility, because never spend 5 minutes doing something by hand when you can fail automating it in 5 hours")

    args.add_argument('-o', '--opencv', required=False, action="store_true", help="Build OpenCV 4 with MinGW, REQUIRED FOR MAKING A WINDOWS RELEASE")
    args.add_argument('-w', '--windows', required=False, action="store_true", help="Make a Windows release using Wine (NEED PYTHON INSTALLED IN THE WINEPREFIX VARIABLE IN THIS FILE)")
    args.add_argument('-l', '--linux', required=False, action="store_true", help="Make a Linux release, potentially for the AUR? (not implemented)")

    args = args.parse_args()

    args = {
        "opencv": args.opencv,
        "windows": args.windows,
        "linux": args.linux,
    }

    RM = ReleaseMaker(args)
    RM.run()
    