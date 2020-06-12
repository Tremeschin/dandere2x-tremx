# Dandere2x Tremx (me) Version

## What is Dandere2x

Dandere2x is a free (as in freedom), open source Linux / Windows "video compressor" that detects image redundancies between every successive frames, generating a "residual" image (the differences) between them and builds the whole video back with this compressed information.

All of this is to make more efficient for expensive raw compute power upscalers (like Waifu2x, SRMD, RealSR) to process a video as they'll only have to process the residual image, the "only-needed" parts of the content rather than each frame individually.

You can get more info on the intuition of this project on the [original Dandere2x wiki](https://github.com/aka-katto/dandere2x/wiki/How-Dandere2x-Works)

Check out aka-katto's repo as well :)

* "What is Dandere2x" video is work in progress

## Tremx version what does that mean?  

I've seen some people having trouble writing my username "Tremeschin" so generally they'll call me "Tremx" or "Tremex" for short, hence why this repository name / "Dandere2x version".

In the past I contributed to the original Dandere2x both with code and ideas, however one day I felt like trying to write my own version of it with the structure and technology I'd use as well as simplifying a lot of code and making it more modular and easier to develop on.

## Why it is used, performance?

Waifu2x, SRMD, RealSR all are good upscalers, a LOT better than image editing ones though they're also a LOT slower. Let's take that 10 seconds sample of the anime Your Name included in the `src/samples` folder: there's 240 total frames, a 480p file takes 1.8 seconds in average to upscale on my GPU, that would be 240 frames * 1.8 seconds = 432 seconds to upscale a 10 second video.

Running only the Dandere2x block matching on the video reveals that there are 246.649 total blocks, 52.399 of those need upscaling.

That is 78.75% of "block recycling" through the video, which should lower that 8 minutes by this amount: 432 seconds * ( 100% - 78.5% ) = 92 seconds, which is about right, upscaling this video takes about 83 seconds on a Dandere2x session here.

So we went from 432 seconds to only 92 seconds, that is 2.6 frames per second!!

Note that this sample video isn't as "static" as most anime, so numbers can be much higher or lower. It will work best with anime as there are less moving images comparing to something like an IRL video.

Generally speaking here's the order of upscaling speed in descending order:

- Anime
- Cartoon
- IRL

## Instructions

Dandere2x should work in both Linux and Windows, though I haven't done much testing on the Windows OS but generally speaking it works with minor issues depending on your setup.

You can help me testing it, reporting bugs or finding fixes

Strongly recommend reading [wiki on Dandere2x settings](https://github.com/Tremeschin/dandere2x-tremx/wiki/Dandere2x-settings) before using the project.

### Windows

#### Running from a release

No releases available right now, it's still very much in WIP and changing quite some core code, it'll be hard to micro manage it :(

#### Running from source

Check out the wiki on [running Dandere2x on Windows](https://github.com/Tremeschin/dandere2x-tremx/wiki/Windows) from the source code!!

### Linux

Dandere2x on Linux must be run directly from the source code, head over to our wiki on [running Dandere2x on Linux](https://github.com/Tremeschin/dandere2x-tremx/wiki/Linux)!!


## What is being worked on? 

### Road to a 1.0 release

- [x] Fix aggressiveness not scaling up with larger block sizes or down with smaller
- [ ] Rewrite `get-externals.py` for a better UX and maintainability
- [ ] Make the GUI more presentable, elegant
- [x] (90%) Automation scripts for making a Windows release with ease (using Wine for pyinstaller?)
- [ ] Write better Failsafe class?
- [ ] GUI hangs one CPU core after upscale finishes sometimes (lol?)
- [ ] Add GUI tooltips on most options
- [ ] Concatenate the partial video files without re-encoding
- [ ] (SERIOUS) Can't exit sesssion if FFmpeg haven't write the start of the piped video, errors when concatenating later on and if remove bad video audio desync
- [x] Add proper math to decide best value for `upscale_full_frame_threshold`

### Issues

- Minor contrast issues on a upscaled videos, this is acknowledged and affects aka's Dandere2x as well

- The best settings and defaults / recommended ones aren't really optimal, they need some love

- I'm not completely sure how compatible OpenCV is reading different video codecs / obscure formats, it worked well on MKV and MP4, there can be some videos that don't get fully upscaled (?)

## Pro Tips

- I cannot stress enough to read through the full wiki page on [Dandere2x settings](https://github.com/Tremeschin/dandere2x-tremx/wiki/Dandere2x-settings) with attention before changing the settings on your own

- Be sure to read the GUI tool tips on the settings by hovering the mouse on them, those have some useful hints in a short amount of text compared to the wiki

## Links

Check out our [subreddit](https://www.reddit.com/r/Dandere2x/)

We also have a [Telegram server](https://t.me/joinchat/KTRznBIPPNCbHkUqnwT8pA)

## Thanks to

Dandere2x utilizes some community driven projects such as:

nihui's Waifu2x Vulkan port https://github.com/nihui/waifu2x-ncnn-vulkan

nihui's SRMD Vulkan port https://github.com/nihui/srmd-ncnn-vulkan 

nihui's RealSR Vulkan port https://github.com/nihui/realsr-ncnn-vulkan

DeadSix27's Waifu2x C++ port https://github.com/DeadSix27/waifu2x-converter-cpp  

opencv https://github.com/opencv/opencv

See requirements.txt for the used packages on the Python programming language

And of course, the original Dandere2x idea, https://github.com/aka-katto
