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

Strongly recommend reading [wiki on Dandere2x settings](https://github.com/Tremeschin/dandere2x-tremx/wiki/Dandere2x-settings) before using the project.

RESUMING SESSION IS A BIT UNSTABLE AT THE MOMENT, PREFERABLY FINISH A SESSION IN A SINGLE RUN

### Windows

#### Running from a release

No releases available right now, it's still very much in WIP and changing quite some core code, it'll be hard to micro manage it :(

#### Running from source

Check out the wiki on [running Dandere2x on Windows](https://github.com/Tremeschin/dandere2x-tremx/wiki/Windows) from the source code!!


### Linux

Dandere2x on Linux must be run directly from the source code, head over to our wiki on [running Dandere2x on Linux](https://github.com/Tremeschin/dandere2x-tremx/wiki/Linux)!!


## What is being worked on? 


### Issues / TODOs / Roadmap

- Minor contrast issues on a upscaled videos, this is acknowledged and affects aka's Dandere2x as well

- Waifu2x is acting weird on Windows, investigating this now as it's the _(last)_ thing to be usable, though some "beta testers" run it fine and others don't

- The best settings and defaults / recommended ones are rough, they need some love

- I'm not completely sure how compatible OpenCV is reading different video codecs / obscure formats, it worked well on MKV and MP4 though MKV is preferred here IMO.

- There's some tweaks we can do to better IRL video quality and speed, those aren't top priority but might come next, maybe a "tldr mode" like: dandere2x_mode: {anime, irl, cartoon} on the settings?  

## Pro Tips

- You can pass the argument `-f` to Dandere2x CLI to force not resume a session, ie. delete its folder and start up again if anything go wrong: `python dandere2x_cli.exe -f`

- Be sure to read carefully the comments on settings.yaml file as I don't have a proper wiki yet :)

## Links

Check out our [subreddit](https://www.reddit.com/r/Dandere2x/)

We also have a [Telegram server](https://t.me/joinchat/KTRznBIPPNCbHkUqnwT8pA)

## Thanks to

Dandere2x utilizes some community driven projects such as:

nihui's Waifu2x https://github.com/nihui/waifu2x-ncnn-vulkan

DeadSix27's Waifu2x https://github.com/DeadSix27/waifu2x-converter-cpp  

opencv https://github.com/opencv/opencv

See requirements.txt for the used packages on the Python programming language

And of course, the original Dandere2x idea, https://github.com/aka-katto
