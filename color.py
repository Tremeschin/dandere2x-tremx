# DRY - Don't Repeat Yourself :)

from sty import fg, bg, ef, rs


def bg_by_name(name):
    return eval("bg.%s" % name)


def color_by_name(name):
    return eval("fg.%s" % name)


def rgb(r, g, b):
    return fg(r, g, b)


def debug_color():
    return rgb(0, 255, 247)


if __name__ == "__main__":
    print("You shouldn't be running this file directly, Dandere2x is class based and those are handled by dandere2x.py which is controlled by dandere2x_cli.py or the upcoming GUI")
