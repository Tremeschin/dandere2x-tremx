"""
===============================================================================

Purpose: Download dependencies for Dandere2x of a minimal / source release

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

# For now this file just works, should rewrite it properly

from utils import Miscellaneous
import requests
import zipfile
import json
import time
import wget
import os


ROOT = os.path.dirname(os.path.abspath(__file__))

externals_folder = ROOT + os.path.sep + "externals"


if not os.path.exists(externals_folder):
    os.mkdir(externals_folder)

# get the release stuff

print("\n Getting github.com/Tremeschin/dandere2x-tremx-externals releases..")

data = requests.get("https://api.github.com/repos/Tremeschin/dandere2x-tremx-externals/releases").json()

release_names = {}

for count, release in enumerate(data):
    release_names[count] = release['name'] 


# get the user input

while True:
    print("\n - Please select the releases you want to download")
    print(" - FFmpeg + FFprobe and Dandere2x C++ are required for Dandere2x to work")
    print(" - Choose one or multiple Waifu2x versions as well.")
    print("\n   (input a csv value like: 0,1,2)\n")

    for index in release_names:
        print("", index, "-", release_names[index])

    uinput = input("\n>> ")

    try:
        todownload = []
        uinput = uinput.split(",")

        for index in uinput:
            todownload.append(release_names[int(index)])
            
        break

    except Exception:
        pass



# get the download links

download_links = {}

for relname in todownload:
    
    for count, release in enumerate(data):
        if release['name'] == relname:
            download_links[release['name']] = release['assets'][0]['browser_download_url']



# download them

eta = 1
currentrelease = ""

def bar_custom(current, total, width=80):
    global currentrelease, startdownload


    #current       -     time.time() - startdownload 
    #total-current -     eta

    #eta ==   (total-current)*(time.time()-startdownload)) / current

    try: # div by zero
        eta = int(( (time.time() - startdownload) * (total - current) ) / current)
    except Exception:
        eta = 0

    avgdown = ( current / (time.time() - startdownload) ) / 1024

    currentpercentage = int(current / total * 100)
    
    print("\r Downloading release [{}]: [{}%] [{:.2f} MB / {:.2f} MB] ETA: [{} sec] AVG: [{:.2f} kB/s]".format(currentrelease, currentpercentage, current/1024/1024, total/1024/1024, eta, avgdown), end='', flush=True)
        


print('\n  Now starting the downloads..\n')

for name, link in download_links.items():
    
    currentrelease = name.replace(" - Static Externals for Dandere2x", "")
    
    savepath = ROOT + os.path.sep + name + ".zip"
    extractpath = ROOT + os.path.sep + "externals"

    if os.path.exists(savepath):
        print("File " + name + " already downloaded.")
        continue

    startdownload = time.time()
    wget.download(link, savepath, bar=bar_custom)
    print("\n")
        

    # extract them

    print("  Extracting the release " + currentrelease + "...", end='')

    with zipfile.ZipFile(savepath, 'r') as zip_ref:
        zip_ref.extractall(extractpath)
    
    print(" finished!!\n\n")

    os.remove(savepath)