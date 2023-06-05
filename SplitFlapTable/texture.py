# Copyright (c) 2023, Mirko Barthauer
# All rights reserved.

# This source code is licensed under the MIT-style license found in the
# LICENSE file in the same directory of this source tree.

import os
import math
from PIL import Image, ImageDraw, ImageFont

def createCharactersTexture(charSpace=(125,200), characters="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-+.?! ", fontPath="bahnschrift.ttf", color="white", background="black", output="characters.png"):
    itemsPerSide = math.ceil(math.sqrt(len(characters)))
    imgSize = (charSpace[0]*itemsPerSide, charSpace[1]*itemsPerSide)
    
    # create the img
    im = Image.new("RGB", imgSize, color=background)
    
    # define the character size and the base line (should be at max .75 of charSpace height, tested on zero = 0)
    targetSize = (int(0.7*charSpace[0]), int(0.65*charSpace[1]))
    charSize = 40
    acceptedError = 0.05
    increment = 2
    maxIt = 100
    i = 0
    font = None 
    while i < maxIt:
        font = ImageFont.truetype(fontPath, charSize)
        bbox = font.getmask("0").getbbox()
        currentSize = (bbox[2], bbox[3])
        error = [abs((currentSize[i]-targetSize[i])/targetSize[i]) for i in range(2)]
        # ending criterion 
        if max(error) <= acceptedError:
            break
        charSize += increment
        i += 1

    # type
    i = 0
    d = ImageDraw.Draw(im)
    for c in characters:
        imChar = Image.new("RGB", charSpace, color=background)
        dChar = ImageDraw.Draw(imChar)
        textWidth, textHeight = dChar.textsize(c, font=font)
        dChar.text((0.5*charSpace[0] - 0.5*textWidth, 0.5*charSpace[1] - 0.5*textHeight), c, color, font)
        col = i % itemsPerSide  
        row = int(i/itemsPerSide)
        boundaries = [col*charSpace[0], row*charSpace[1], (col+1)*charSpace[0], (row+1)*charSpace[1]]
        d.rectangle(boundaries, fill=background, outline=color)
        im.paste(imChar, (boundaries[0], boundaries[1]))
        i += 1

    # save
    im.save(output)


def findFont(name):
    result = None
    if not "." in name:
        name = name + ".ttf"
    fonts = getFonts()
    if name in fonts:
        result = os.path.join(os.path.join(os.environ['WINDIR'],'fonts', name))
    elif name.lower() in fonts:
        result = os.path.join(os.path.join(os.environ['WINDIR'],'fonts', name.lower()))
    else:
        print("Could not find font %s" % name)
    return result


def getFonts():
    return [value for value in os.listdir(os.path.join(os.environ['WINDIR'],'fonts')) if value.endswith(".ttf")]

if __name__ == "__main__":
    fontPath = findFont("bahnschrift.ttf")
    if fontPath is not None:
        createCharactersTexture(fontPath=fontPath)