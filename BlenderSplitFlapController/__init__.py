import bpy.utils

from .control import SplitFlapSettings, SplitFlapKeySettings, SplitFlapPanel, SplitFlapAnimationPanel, SplitFlapApplyFrames, SplitFlapAnimationListItem, SplitFlapAnimationList, SplitFlapController, SplitFlapAnimationController

bl_info = {
    "name": "Split Flap Table Generator",
    "description": "Test",
    "author": "MB",
    "version": (0, 0, 1),
    "blender": (3, 4, 0),
    "location": "View3D",
    "warning": "", # used for warning icon and text in addons panel
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
        self.report({'ERROR'}, "Please install the python module pillow in your Blender python before.")
        return
    
    for cls in classes:
        print("register %s" % str(cls))
        bpy.utils.register_class(cls)
    bpy.types.Collection.splitFlapSettings = SplitFlapSettings
    bpy.types.Scene.splitFlapTool = bpy.props.PointerProperty(type=SplitFlapSettings)
    bpy.types.Scene.splitFlapKeySetting = bpy.props.PointerProperty(type=SplitFlapKeySettings)
    bpy.types.Scene.splitFlapAnimations = bpy.props.PointerProperty(type=SplitFlapAnimationList)
    bpy.types.Scene.splitFlapAnimationIndex = bpy.props.IntProperty(name = "Index for SplitFlapAnimationList", default = 0)

def unregister():
    del bpy.types.Scene.splitFlapTool
    del bpy.types.Scene.splitFlapKeySetting
    del bpy.types.Scene.splitFlapAnimations
    del bpy.types.Scene.splitFlapAnimationIndex
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    

if __name__ == "__main__":
    register()