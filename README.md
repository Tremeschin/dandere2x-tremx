# Dandere2x Tremx (me) Version

## What is Dandere2x
WIP
## Instructions

### Linux
I currently _officially_ support distros with the pacman package manager as it's a bit tricky in my opinion to get a working Waifu2x on other distros, but it should work if you got one.

You'll want four things:
1. Waifu2x
2. Python 3
3. A compiler (g++ preferred)
4. OpenCV 4 package

There's two packages on the AUR for Waifu2x that I use, `waifu2x-ncnn-vulkan` and `waifu2x-converter-cpp`, I'd personally use the vulkan one only.

You should already have Python 3 installed, if not the instructions are based on your package manager like for apt: `sudo apt install python` or pacman: `sudo pacman -S python`. You'll also need pip, for pacman `sudo pacman -S python-pip`

The compiler should be bundled in the base system of yours, just type `g++` on a terminal and see if it outputs anything, if not you should install the gcc package. For pacman I'd personally do `sudo pacman -S base-devel`

The opencv4 just install it with `sudo pacman -S opencv`, it should install the latest version 4.

Now download this repository or `git clone https://github.com/Tremeschin/dandere2x-tremx` into a folder, `cd` into it then:

1. `pip install -r requirements.txt --user`
2. `sh ./dandere2x_cpp_tremx/linux_compile.sh`

And you should be ready to go run it with `python dandere2x_cli.py`, change the `settings.yaml` to your needs before using it

GUI is WIP

### Windows

#### Running from source

You'll need to install Python 3.8, and on its the installer check the box to add Python to PATH before installing it: https://www.python.org/

Now either download or clone the repository, there's a download button on the main repository page or you could install git and open a git shell into a folder and `git clone https://github.com/Tremeschin/dandere2x-tremx`.

Now open a shell into the `dandere2x-tremx` folder, run `pip install -r requirements.txt`

You'll need to download the externals dependencies, luckily I've set up a repo with all the files required so just run `python get_externals.py` and you'll be prompted to download the dependencies.

You'll definelty want to download "Dandere2x C++", "FFmpeg + FFprobe" and one Waifu2x flavour, I only implemented DeadSix27's CPP and nihui's ncnn Vulkan versions; I personally only use the Vulkan one.

Now edit the file `settings.yaml` to your needs and run Dandere2x with `python dandere2x_cli.py`

## Pro Tips

You can pass the argument `-f` to Dandere2x CLI to force not resume a session, ie. delete its folder and start up again if anything go wrong: `python dandere2x_cli.exe -f`

#### Running from a release
NOT DONE YET, NO RELEASES

