from PIL import Image

OUTPUT_SIZE = 200, 200


def convert(filename):

    im = Image.open(filename)

    w, h = im.size

    if w > h:
        im = im.crop(((w - h) // 2, 0, w - (w - h) // 2, h))
    elif h > w:
        im = im.crop((0, (h - w) // 2, w, h - (h - w) // 2))

    im = im.resize(OUTPUT_SIZE)

    im.save(filename)





