# Copyright (c) 2023, Mirko Barthauer
# All rights reserved.

# This source code is licensed under the MIT-style license found in the
# LICENSE file in the same directory of this source tree.

import bpy.utils

from .structures import SplitFlapSettings, SplitFlapKeySettings
from .control import SplitFlapPanel, SplitFlapAnimationPanel, SplitFlapApplyFrames, SplitFlapAnimationListItem, SplitFlapAnimationList, SplitFlapController, SplitFlapAnimationController

bl_info = {
    "name": "Split Flap Table Generator",
    "description": "Creates split flap tables like for classic railway and airport departure boards and creates the animation of switching from one string on display to the next. Can be customised by choosing the font, characters and font/background colours.",
    "author": "Mirko Barthauer <m.barthauer@t-online.de>",
    "version": (0, 0, 1),
    "blender": (3, 4, 0),
    "location": "View3D",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "3D View"
}

classes = (SplitFlapSettings, SplitFlapKeySettings, SplitFlapPanel, SplitFlapAnimationPanel, SplitFlapApplyFrames,
            SplitFlapAnimationListItem, SplitFlapAnimationList, SplitFlapController, SplitFlapAnimationController)

def register():
    try:
        import PIL
    except ModuleNotFoundError as e:
        self.report({'ERROR'}, "Please install the python module pillow in your Blender python beforehand.")
        return
    
    for cls in classes:
        print("register %s" % str(cls))
        bpy.utils.register_class(cls)
    bpy.types.Collection.splitFlapSettings = SplitFlapSettings
    bpy.types.Scene.splitFlapTemplate = bpy.props.StringProperty(name = "ID of the last loaded template flap item", default="")
    bpy.types.Scene.cardTemplate = bpy.props.StringProperty(name = "ID of the last loaded card item", default="")
    bpy.types.Scene.splitFlapTool = bpy.props.PointerProperty(type=SplitFlapSettings)
    bpy.types.Scene.splitFlapKeySetting = bpy.props.PointerProperty(type=SplitFlapKeySettings)
    bpy.types.Scene.splitFlapAnimations = bpy.props.PointerProperty(type=SplitFlapAnimationList)
    bpy.types.Scene.splitFlapAnimationIndex = bpy.props.IntProperty(name = "Index for SplitFlapAnimationList", default = -1, update=structures.flapAnimation_updateDisplay)

def unregister():
    del bpy.types.Scene.splitFlapTemplate
    del bpy.types.Scene.cardTemplate
    del bpy.types.Scene.splitFlapTool
    del bpy.types.Scene.splitFlapKeySetting
    del bpy.types.Scene.splitFlapAnimations
    del bpy.types.Scene.splitFlapAnimationIndex
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    

if __name__ == "__main__":
    register()