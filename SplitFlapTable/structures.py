# Copyright (c) 2023, Mirko Barthauer
# All rights reserved.

# This source code is licensed under the MIT-style license found in the
# LICENSE file in the same directory of this source tree.
import bpy
from .texture import getFonts

def flapSettings_getFonts(scene, context):
    items = []
    fonts = getFonts()
    for font in fonts:
        items.append((font, font, "available font"))
    return items

def flapSettings_updateFont(self, context):
    self.fontName = self.fontChoice

def flapAnimation_updateDisplay(self, context):
    index = self.splitFlapAnimationIndex
    item = self.splitFlapAnimations.items[index]
    #print("updateDisplay, set %s %.2f" % (item.text, item.keyTime))
    self.splitFlapKeySetting.text = item.text
    self.splitFlapKeySetting.keyTime = item.keyTime

def keySettings_poll(self, object):
    return object["SplitFlap"] is not None

def keySettings_update(self, context):
    self.collectionID = self.collection.name

class SplitFlapSettings(bpy.types.PropertyGroup):
    rowCount : bpy.props.IntProperty(
        name = "Row count",
        description="Number of rows of split flap items",
        default = 1,
        min = 1,
        max = 10
    )
    colCount : bpy.props.IntProperty(
        name = "Column count",
        description="Number of columns of split flap items",
        default = 12,
        min = 1,
        max = 100
    )
    horizontalGap : bpy.props.FloatProperty(
        name = "Horizontal gap",
        description = "Horizontal gap between flaps in meters",
        default = 0.02,
        min = 0.01,
        max = 1.
    )
    verticalGap : bpy.props.FloatProperty(
        name = "Vertical gap",
        description = "Vertical gap between flaps in meters",
        default = 0.04,
        min = 0.01,
        max = 1.
    )
    flapRadius : bpy.props.FloatProperty(
        name = "Flap radius",
        description = "Radius in meters of the flap circle",
        default = 0.02,
        min = 0.005,
        max = 1.
    )
    flapTime : bpy.props.FloatProperty(
        name = "Flap time",
        description = "Time in seconds to flap one card further",
        default = 0.1,
        min = 0.1,
        max = 1.
    )
    characters : bpy.props.StringProperty(
        name="Characters",
        description="Available characters in every split flap item",
        default="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-+.?! ",
        maxlen=1024,
    )
    charWidth : bpy.props.FloatProperty(
        name = "Relative char width",
        description = "Relative part of the flap width the char should fill at most",
        default = 0.7,
        min = 0.3,
        max = 1.5
    )
    charHeight : bpy.props.FloatProperty(
        name = "Relative char height",
        description = "Relative part of the flap height the char should fill at most",
        default = 0.7,
        min = 0.3,
        max = 1.5
    )
    flapRatio : bpy.props.FloatProperty(
        name = "Flap item width/height ratio",
        description = "Ratio of the width of the flap item divided by twice the height (upper and lower characters parts counted as one)",
        default = 0.5,
        min = 0.2,
        max = 1.5
    )
    fontName : bpy.props.StringProperty(
        name="Font",
        description="Font to use for the characters",
        default="Bahnschrift",
        maxlen=1024,
    )
    fontChoice : bpy.props.EnumProperty(
        name="Font",
        description="Font to use for the characters",
        items=flapSettings_getFonts,
        update=flapSettings_updateFont
    )
    identPrefix : bpy.props.StringProperty(
        name="Identifier",
        description="Preferred identifier (prefix) for the collection and its split flap items",
        default="SplitFlap",
        maxlen=1024,
    )
    fontColor : bpy.props.FloatVectorProperty(
        name="Font color",
        subtype = "COLOR",
        description="Color of the letters of the split flap items",
        default=(1.0,1.0,1.0)
    )
    backgroundColor : bpy.props.FloatVectorProperty(
        name="Background color",
        subtype = "COLOR",
        description="Base color of the split flap items",
        default=(1.0,0.0,0.0)
    )
    createFrame : bpy.props.BoolProperty(
        name = "Create frame",
        description = "Create a frame shape to house the flaps",
        default = False
    )
    
    
class SplitFlapKeySettings(bpy.types.PropertyGroup):
    text : bpy.props.StringProperty(
        name="Original text input",
        description="Original text input by the user",
        default="",
        maxlen=1024,
    )
    formattedText : bpy.props.StringProperty(
        name="Text to display",
        description="Text to display when the split flap collection is initialised, taking into account the available characters",
        default="",
        maxlen=1024,
    )
    keyTime : bpy.props.FloatProperty(
        name = "Time key",
        description = "Time in seconds when the flap starts switching to the target text",
        default = 5,
        min = 0,
        max = 240
    )
    extend : bpy.props.BoolProperty(
        name = "Fill with space",
        description = "Fill texts shorter than the flip collection with space characters",
        default = True
    )
    center : bpy.props.BoolProperty(
        name = "Center text",
        description = "Add space characters such that the given text is centered",
        default = False
    )
    collectionID : bpy.props.StringProperty(
        name="Collection ID",
        description="The ID of the split flap collection this key setting should be applied to",
        default="",
        maxlen=1024,
    )
    collection : bpy.props.PointerProperty(
        name="Chosen collection",
        type=bpy.types.Collection,
        description="",
        poll=keySettings_poll,
        update=keySettings_update,
    )
    selected : bpy.props.BoolProperty(
        name="Selected",
        description="Marker to remember if currrently selected in the UI",
        default = False
    )
