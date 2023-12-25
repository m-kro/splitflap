# Copyright (c) 2023, Mirko Barthauer
# All rights reserved.

# This source code is licensed under the MIT-style license found in the
# LICENSE file in the same directory of this source tree.

import os
import math
from PIL import Image, ImageDraw, ImageFont

def createCharactersTexture(charSpace=(120,200), characters="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-+.?! ", fontPath="bahnschrift.ttf", color="white", background="black", output="characters.png", fontFactorWidth=0.7, fontFactorHeight=0.65, itemsPerSide=None):
    if itemsPerSide is None:
        itemsPerSide = math.ceil(math.sqrt(len(characters)))
    imgSize = (charSpace[0]*itemsPerSide, charSpace[1]*itemsPerSide)
    
    # create the img
    im = Image.new("RGB", imgSize, color=background)
    
    # define the character size and the base line (should be at max .75 of charSpace height, tested on zero = 0)
    targetSize = (int(fontFactorWidth*charSpace[0]), int(fontFactorHeight*charSpace[1]))
    charSize = 40
    increment = 2
    maxIt = 100
    i = 0
    font = None
    
    # get the widest character
    font = ImageFont.truetype(fontPath, charSize)
    charWidths = [(font.getmask(character).getbbox())[2] - (font.getmask(character).getbbox())[0] if character != ' ' else 0 for character in characters]
    #print("%s" % "\n".join(["%s: %d" % (characters[i], charWidths[i]) for i in range(len(charWidths))]))
    widestChar = characters[charWidths.index(max(charWidths))]
    #print("Widest char: %s" % widestChar)
    
    while i < maxIt:
        font = ImageFont.truetype(fontPath, charSize)
        bbox = font.getmask(widestChar).getbbox()
        currentSize = (bbox[2], bbox[3])
        # ending criterion 
        if currentSize[0]-targetSize[0]>=0 or currentSize[1]-targetSize[1]>=0:
            #print("Stop char heuristic: %s target size %s actual size %s" % (widestChar, str(targetSize), str(currentSize)))
            break
        charSize += increment
        i += 1

    # type
    i = 0
    d = ImageDraw.Draw(im)
    deprecatedSize = getattr(d, "textsize", None) is None # pillow API change in v.10
    for c in characters:
        imChar = Image.new("RGB", charSpace, color=background)
        dChar = ImageDraw.Draw(imChar)
        if deprecatedSize:
            left, top, right, bottom = dChar.textbbox((0,0), c, font=font)
            print("left %.0f top %.0f right %.0f bottom %.0f" % (left, top, right, bottom))
            textWidth = right - left
            textHeight = bottom - top
        else:
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