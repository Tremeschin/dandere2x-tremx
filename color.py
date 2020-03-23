from sty import fg, bg, ef, rs


def color_by_name(name):
    return eval("fg.%s" % name)

    
def rgb(r, g, b):
    return fg(r, g, b)


def debug_color():
    return rgb(0, 255, 247)