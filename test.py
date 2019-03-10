def spph(elem):
    h = 0
    for i in elem:
        h += ord(i) * len(elem)**2
    return h
