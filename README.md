# Dandere2x Tremx (me) Version

## What is Dandere2x

Dandere2x is a Linux / Windows video "compressor" that detects image redundancies between every successive frames, generating a "residual" image (the differences) between then and builds the whole video back with this compressed information.

All of this is to make more efficient for computation expensive upscalers (we use Waifu2x) to process a video as there will be only the need to compute these residual images, the "only-needed" parts of the content rather than each frame individually.

You can get more info on the intuition of this project on the original Dandere2x wiki https://github.com/aka-katto/dandere2x/wiki/How-Dandere2x-Works

Check out aka-katto's repo as well :)

"What is Dandere2x" video is work in progress

## Tremx version what does that mean?  

I've seen some people having trouble writing my username "Tremeschin" so generally they'll call me "Tremx" or "Tremex" for short, hence why this repository name / "Dandere2x version".

In the past I contributed to the original Dandere2x both with code and ideas, however one day I felt like trying to write my own version of it with the structure and technology I'd use as well as simplifying a lot of code and making it more modular and easier to develop on.

## Why it is used, performance?

Waifu2x is a good upscaler, though it's really slow for videos. Let's take that 10 seconds sample of the anime Your Name: there's 240 total frames, a 480p file takes 1.8 seconds in average to upscale on my GPU, that would be 240 frames * 2 seconds = 432 seconds to upscale a 10 second video.

Running Dandere2x block matching only on the video, reveals that there is 246,649 total blocks, 52,399 of those need upscaling, that is 78.75% of "block recycling" through the video, which should lower that 8 minutes by this amount: 432 seconds * ( 1 - 0.785 ) = 92 seconds, which is about right, upscaling this video takes about 83 seconds on a Dandere2x session here.

Fun number: 240 frames / 92 seconds = 2.6 frames per second on average we're processing the video.

So we went from 432 seconds to only 83 seconds. Note that this sample video isn't as "static" as most anime, so numbers can be higher or lower. It will work best with anime as there are more static images comparing to something like an IRL video.

Generally speaking here's the order of upscaling speed in descending order:

- Anime
- Cartoon
- IRL

## Instructions

Dandere2x should work in both Linux and Windows, though I haven't done much testing on the Windows OS, it's a bit unstable at the moment.  

You can help me testing it, reporting bugs or finding fixes

### Windows

#### Running from a release

No releases available right now, it's still very much in WIP and changing quite some core code, it'll be hard to micro manage it :(

#### Running from source

You'll need to install Python 3.8, be sure to check the box to add Python to PATH while installing it: https://www.python.org/ 

Now either download or clone the repository, there's a download button on the main repository page or you could install git and open a git shell into a folder and `git clone https://github.com/Tremeschin/dandere2x-tremx`

Now open a shell into the `dandere2x-tremx` folder, run `pip install -r requirements.txt`

You'll need to download the externals dependencies, luckily I've set up a repo with all the files required so just run `python get_externals.py` and you'll be prompted to download the dependencies.  

You'll definitely want to download "Dandere2x C++", "FFmpeg + FFprobe" and one Waifu2x "flavour", I've only implemented DeadSix27's C++ and nihui's ncnn Vulkan versions; I personally only use the Vulkan one as it's the less troublesome and faster one.

You can run it by a (not really tested) CLI script, see `python dandere2x_cli.py -h` for the available options.

I think it's better to edit the file `settings.yaml` to your needs and run Dandere2x with only `python dandere2x_cli.py`

This file is well documented, you should be able to guide yourself through it.

Be sure to read some pro tips at the end of this README as well :)


### Linux

I currently _officially_ support distros with the pacman package manager as it's a bit tricky in my opinion to get a working Waifu2x on other distros, but it should work if you got one.

#### Requirements

You'll want four things:

1. Waifu2x

2. Python 3

3. A compiler (g++ preferred from the gcc package)

4. OpenCV 4 package

For pacman it's easily done with the following:

- `sudo pacman -S base-devel opencv python python-pip waifu2x-ncnn-vulkan-git`

You probably need to install the Vulkan loaders / headers as well if you're on a AMD GPU (not sure about NVIDIA, they might be already bundles in their proprietary driver?): 

 - `sudo pacman -S vulkan-headers vulkan-icd-loader lib32-vulkan-icd-loader vulkan-radeon lib32-vulkan-radeon`

There's two packages on the AUR for Waifu2x that I use, `waifu2x-ncnn-vulkan` and `waifu2x-converter-cpp`, I'd personally use the Vulkan one only as it is on the above command. If you GPU doesn't support 
  
You should already have Python 3 installed, if not the instructions are based on your package manager. You'll also need pip for installing the dependencies.

Same for the OpenCV 4 and Waifu2x, you should be able to find yourself on yours distribution I hope.

The compiler should be bundled in the base system of yours, just type `g++` on a terminal and see if it outputs anything, if not you should install the gcc package.
  
#### Building

Now download this repository or `git clone https://github.com/Tremeschin/dandere2x-tremx` into a folder, then change current working directory to it.

We'll be installing Python modules dependencies and compiling the C++ part of Dandere2x now, there's a script to compile and move the binary to the right place, don't worry, just have the dependencies set up correctly.

If you like you can install these dependencies on a virtual env with Python, though I don't really use them / know how to :v

- `pip install -r requirements.txt --user`

- `sh ./dandere2x_cpp_tremx/linux_compile.sh`

And you should be ready to go

#### Running

You can run it by a (not really tested) CLI script, see `python dandere2x_cli.py -h` for the available options.

I think it's better to edit the file `settings.yaml` to your needs and run Dandere2x with only `python dandere2x_cli.py`

This file is well documented, you should be able to guide yourself through it.
  

## What is being worked on? 


### Issues / TODOs / Roadmap

- A GUI is slowly making progress, though I'm not sure if I'll stick with GTK, it's half working right now.. `python gui.py` if you wanna test it, might only work on Linux OS with GTK package installed tho

- Minor contrast issues on a upscaled videos, this is acknowledged and affects aka's Dandere2x as well

- Waifu2x is acting weird on Windows, investigating this now as it's the _(last)_ thing to be usable, though some "beta testers" run it fine and others don't

- The best settings and defaults / recommended ones are rough, they need some love

- I'm not completely sure how compatible OpenCV is reading different video codecs / obscure formats, it worked well on MKV and MP4 though MKV is preferred here IMO.

- There's some tweaks we can do to better IRL video quality and speed, those aren't top priority but might come next, maybe a "tldr mode" like: dandere2x_mode: {anime, irl, cartoon} on the settings?  

## Pro Tips

- You can pass the argument `-f` to Dandere2x CLI to force not resume a session, ie. delete its folder and start up again if anything go wrong: `python dandere2x_cli.exe -f`

- Be sure to read carefully the comments on settings.yaml file as I don't have a proper wiki yet :)

## Thanks to

Dandere2x utilizes some community driven projects such as:

nihui's Waifu2x https://github.com/nihui/waifu2x-ncnn-vulkan

DeadSix27's Waifu2x https://github.com/DeadSix27/waifu2x-converter-cpp  

opencv https://github.com/opencv/opencv

See requirements.txt for the used packages on the Python programming language

And of course, the original Dandere2x idea, https://github.com/aka-katto
