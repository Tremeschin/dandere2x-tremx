from vapoursynth import core
video = core.ffms2.Source(source="[INPUT]")
video = core.std.Transpose(video)
video.set_output()