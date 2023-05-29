import os
import bpy
import math
import addon_utils

from .texture import createCharactersTexture, findFont

class SplitFlapPanel(bpy.types.Panel):
    bl_label = "SplitFlap Panel"
    bl_idname = "OBJECT_PT_SplitFlapPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type= "UI"
    bl_category = "Split Flap"
    # bl_parent_id = ""
    
    def draw(self, context):
        layout = self.layout
        sfTool = context.scene.splitFlapTool
        row = layout.row()
        row.prop(sfTool, "rowCount")
        row = layout.row()
        row.prop(sfTool, "colCount")
        row = layout.row()
        row.prop(sfTool, "horizontalGap")
        row = layout.row()
        row.prop(sfTool, "verticalGap")
        row = layout.row()
        row.prop(sfTool, "flapRadius")
        row = layout.row()
        row.prop(sfTool, "flapTime")
        row = layout.row()
        row.prop(sfTool, "characters")
        row = layout.row()
        row.prop(sfTool, "fontName")
        row = layout.row()
        row.prop(sfTool, "identPrefix")
        row = layout.row()
        row.prop(sfTool, "fontColor")
        row = layout.row()
        row.prop(sfTool, "backgroundColor")
        row = layout.row()
        #row.label(text="SplitFlapController")
        row.operator("object.splitflapcontroller")


class SplitFlapAnimationPanel(bpy.types.Panel):
    bl_label = "SplitFlapAnimation Panel"
    bl_idname = "OBJECT_PT_SplitFlapAnimationPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type= "UI"
    bl_category = "Split Flap"
    # bl_parent_id = ""

    def draw(self, context):
        layout = self.layout
        sfKeySetting = context.scene.splitFlapKeySetting
        row = layout.row()
        row.template_list("OBJECT_UL_SplitFlapAnimationListItem", "", bpy.context.scene.splitFlapAnimations, "items", 
                            bpy.context.scene, "splitFlapAnimationIndex", rows=2, maxrows=5, type='DEFAULT')
        row = layout.row()
        row.prop(sfKeySetting, "text")
        row = layout.row()
        row.prop(sfKeySetting, "keyTime")
        row = layout.row()
        row.prop(sfKeySetting, "extend")
        #row = layout.row()
        #row.prop(sfKeySetting, "collectionID", expand=True)
        row = layout.row()
        row.prop(sfKeySetting, "collection", expand=True)
        row = layout.row()
        #row.label(text="SplitFlapAnimationController")
        row.operator("object.splitflapanimationcontroller", text="add entry").action='ADD'
        row.operator("object.splitflapanimationcontroller", text="update entry").action='UPDATE'
        row.operator("object.splitflapanimationcontroller", text="remove entry").action='DELETE'
        row = layout.row()
        #row.label(text="SplitFlapApplyFrames")
        row.operator("object.splitflapapplyframes")


class SplitFlapAnimationListItem(bpy.types.UIList):
    bl_label = "SplitFlapAnimation List Item"
    bl_idname = "OBJECT_UL_SplitFlapAnimationListItem"

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            #print(item)
            layout.label(text="%s (%s t %.2f)" % (item.text, item.collectionID, item.keyTime))
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="")


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
    fontName : bpy.props.StringProperty(
       name="Font",
       description="Font to use for the characters",
       default="Bahnschrift",
       maxlen=1024,
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

def keySettings_poll(self, object):
    return object["SplitFlap"] is not None

def keySettings_update(self, context):
    self.collectionID = self.collection.name

class SplitFlapKeySettings(bpy.types.PropertyGroup):
    text : bpy.props.StringProperty(
        name="Text to display",
        description="Text to display when the split flap collection is initialised",
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

class SplitFlapAnimationList(bpy.types.PropertyGroup):
    itemIndex : bpy.props.IntProperty(name="itemIndex", default=0)
    items : bpy.props.CollectionProperty(name="items", type=SplitFlapKeySettings)

# TODO: add variants to update and delete frames
class SplitFlapAnimationController(bpy.types.Operator):
    bl_idname = "object.splitflapanimationcontroller"
    bl_label = "Add Split Flap Animation"
    # TODO: see https://b3d.interplanety.org/en/calling-functions-by-pressing-buttons-in-blender-custom-ui/
    action: EnumProperty(
        items=[
            ('DELETE', 'remove entry', 'remove entry'),
            ('UPDATE', 'update entry', 'update entry'),
            ('ADD', 'add entry', 'add entry')
        ]
    )
    
    def execute(self, context):
        sfKeySetting = context.scene.splitFlapKeySetting
        sfAnimations = context.scene.splitFlapAnimations
        added = False
        if len(sfKeySetting.collectionID) > 0 and sfKeySetting.collectionID in bpy.data.collections:
            # check if there is already an entry for the same time
            frameSettings = [frame for frame in sfAnimations.items if frame.collectionID == sfKeySetting.collectionID and abs(frame.keyTime - sfKeySetting.keyTime) < 0.1]
            print(str(frameSettings))
            if len(frameSettings) == 0:
                item = sfAnimations.items.add()
                sfAnimations.itemIndex = len(sfAnimations.items) - 1
                item.text = sfKeySetting.text
                item.keyTime = sfKeySetting.keyTime
                item.extend = sfKeySetting.extend
                item.center = sfKeySetting.center
                item.collectionID = sfKeySetting.collectionID
                added = True
        if not added:
            self.report({'INFO'}, "The item could not be added due to missing input or duplicated data.")
        return {'FINISHED'}


class SplitFlapApplyFrames(bpy.types.Operator):
    bl_idname = "object.splitflapapplyframes"
    bl_label = "Split Flap Apply Frames"
    
    def execute(self, context):
        frameBefore = context.scene.frame_current
        sfKeySetting = context.scene.splitFlapKeySetting
        sfAnimations = context.scene.splitFlapAnimations
        collID = sfKeySetting.collectionID # apply settings of the current collection
        frameSettings = [frame for frame in sfAnimations.items if frame.collectionID == collID]
        frameSettings.sort(key=lambda frame:frame.keyTime)
        fps = bpy.context.scene.render.fps / bpy.context.scene.render.fps_base
        
        if collID in bpy.data.collections:
            coll = bpy.data.collections[collID]
            # remove previous settings
            for obj in coll.all_objects:
                obj.animation_data_clear ()
                # reset rotation to 0
                for modifier in obj.modifiers:
                    if modifier.type == 'NODES' and modifier.name == "SplitFlapCircle":
                        modifier["Input_8"] = 0.
            
            # compute frames: angle for every split flap
            flapTime =  coll["SplitFlapSettings.flapTime"]
            characters = coll["SplitFlapSettings.characters"]
            startChar = characters[0]
            lastFrame = []
            maxLen = len(coll.all_objects)
            startIdx = characters.index(startChar) if startChar in characters else 0
            spaceIdx = characters.index(" ") if " " in characters else 0
            lastString = startChar * len(coll.all_objects)
            
            for frameSetting in frameSettings:
                # check lower/upper case and replace automatically if one of them is not present in the character set
                singleChars = [c for c in frameSetting.text]
                for j in range(0, len(singleChars)):
                    if singleChars[j] not in characters:
                        if islower(singleChars[j]) and upper(singleChars[j]) in characters:
                            singleChars[i] = upper(singleChars[j])
                        elif isupper(singleChars[j]) and lower(singleChars[j]) in characters:
                            singleChars[i] = lower(singleChars[j])
                frameSetting.text = "".join(singleChars)
                i = 0
                if frameSetting.extend:
                    targetString = frameSetting.text[:maxLen] if len(frameSetting.text) >= maxLen else frameSetting.text + " " * (maxLen - len(frameSetting.text))
                elif frameSetting.center:
                    textLen = len(frameSetting.text)
                    if textLen >= maxLen:
                        targetString = frameSetting.text[:maxLen]
                    else:
                        indent = (maxLen - textLen)//2
                        remainder = maxLen - indent - textLen
                        targetString = " " * indent + frameSetting.text + " " * remainder
                else:
                    targetString = "%s%s" % (frameSetting.text[:maxLen], lastString[len(frameSetting.text):])
                startFrame = int(round(fps * frameSetting.keyTime))
                print("lastString '%s' targetString '%s'" % (lastString, targetString))
                
                frameDurations = []
                
                for obj in coll.all_objects:
                    if lastString[i] == targetString[i]:
                        print("Skip remaining character '%s' at index %d" % (lastString[i], i))
                        i += 1
                        continue
                    currentIdx = characters.index(lastString[i])
                    nextIdx = characters.index(targetString[i])
                    if currentIdx < 0 or nextIdx < 0:
                        print("Cannot find a character in the given alphabet '%s'" % characters)
                        i += 1
                        continue
                    idxDiff = nextIdx - currentIdx if nextIdx > currentIdx else nextIdx + len(characters) - currentIdx
                    angleDiff = 2 * math.pi * idxDiff/len(characters)
                    flapFrames = int(round(fps * idxDiff * flapTime))
                    endFrame = startFrame + flapFrames
                    for modifier in obj.modifiers:
                        if modifier.type == 'NODES' and modifier.name == "SplitFlapCircle":
                            if frameSetting.keyTime > 0.01:
                                modifier.keyframe_insert(data_path='["Input_8"]',frame=startFrame)
                            print("Change from '%s' to '%s' at index %d: index diff %d angle %.2f + %.2f at frame %d" % (lastString, targetString, i, idxDiff, modifier["Input_8"], angleDiff, startFrame))
                            modifier["Input_8"] += angleDiff
                            modifier.keyframe_insert(data_path='["Input_8"]',frame=endFrame)
                            lastString = lastString[:i] + targetString[i] + lastString[i + 1:]
                            break
                    i += 1
                    frameDurations.append(flapFrames)
                maxDur = max(frameDurations)
        context.scene.frame_set(frameBefore) # set frame back to begin
        return {'FINISHED'}


class SplitFlapController(bpy.types.Operator):
    bl_idname = "object.splitflapcontroller"
    bl_label = "Split Flap Controller"
    #bl_options = {'REGISTER', 'UNDO'}
    
    # template for split flaps
    templateFile : bpy.props.StringProperty(default="splitFlapTemplate.blend")
    templatePath : bpy.props.StringProperty(default='')
    innerPath = "Object"
    objectName = "SplitFlapItem"
    materialName = "Mat.Flapcard"
    collectionMarker = "SplitFlap"
    
    def execute(self, context):
        # find directory to save the font to
        if not bpy.data.is_saved:
            self.report({'ERROR'}, "Please save the blend file first to indicate the texture storage directory.")
            return {'FINISHED'}
        # look for template file if still undefined
        if len(self.templatePath) == 0:
            for mod in addon_utils.modules():
                if mod.bl_info.get("name") == "Split Flap Table Generator":
                    self.templatePath = os.path.join(os.path.dirname(mod.__file__), self.templateFile)
                    break
        if len(self.templatePath) == 0:
            self.report({'INFO'}, "Cannot find the template blend file %." % self.templateFile)
            return
        oldObjectNames = [obj.name for obj in context.scene.objects]
        bpy.ops.wm.append(
            filepath=os.path.join(self.templatePath, self.innerPath, self.objectName),
            directory=os.path.join(self.templatePath, self.innerPath),
            filename=self.objectName
        )
        # import material too
        with bpy.data.libraries.load(self.templatePath) as (dataFrom, dataTo):
            dataTo.materials = dataFrom.materials
        # pass the current SplitFlapProperties to Geometry Nodes input where necessary
        newObjectNames = [obj.name for obj in context.scene.objects if obj.name not in oldObjectNames and obj.name.startswith(self.objectName)]
        sfTool = context.scene.splitFlapTool
        
        # generate texture
        fontPath = findFont(sfTool.fontName)
        texturePath = None
        textureFile = "FlapCharacters.png"
        if fontPath is None:
            self.report({'ERROR'}, "The font %s could not be found." % sfTool.fontName)
            return {'FINISHED'}
        
        # generate texture
        texturePath = os.path.join(bpy.path.abspath("//"), textureFile)
        fontColor = [min(255, int(255*round(value))) for value in [sfTool.fontColor.r, sfTool.fontColor.g, sfTool.fontColor.b]]
        fontColor.append(255)
        backgroundColor = [min(255, int(255*round(value))) for value in [sfTool.backgroundColor.r, sfTool.backgroundColor.g, sfTool.backgroundColor.b]]
        backgroundColor.append(255)
        createCharactersTexture(characters=sfTool.characters, fontPath=fontPath, output=texturePath, color=tuple(fontColor), background=tuple(backgroundColor))
        
        splitFlapItems = []
        prefix = '' if " " in sfTool.identPrefix else sfTool.identPrefix
        for newObjectName in newObjectNames:
            newObj = bpy.data.objects[newObjectName]
            for modifier in newObj.modifiers:
                if modifier.type == 'NODES' and modifier.name == "SplitFlapCircle":
                    splitFlapItems.append(newObj)
                    modifier["Input_3"] = sfTool.flapRadius
                    modifier["Input_8"] = 0.
                    # rename object according to the wanted prefix
                    newObj.name = "%sItem0" % prefix
                    break

        # make the wanted number of copies and add them to the same collection
        if len(splitFlapItems) == 1:
            # update material of the template: load the image, get the material, copy and change the image
            # find the right material
            for slot in splitFlapItems[0].material_slots:
                if slot.material.name == self.materialName:
                    slot.material.node_tree.nodes["Image Texture"].image = bpy.data.images.load(texturePath)
                    break
            
            # get width and height of the split flap item
            width = splitFlapItems[0].dimensions.x
            height = splitFlapItems[0].dimensions.z
            d = 1
            for h in range(0, sfTool.colCount):
                for v in range(0, sfTool.rowCount):
                    if h == 0 and v == 0:
                        continue
                    objCopy = duplicateObject(splitFlapItems[0])
                    objCopy.name = "%sItem%d" % (sfTool.identPrefix, d)
                    objCopy.location.x = splitFlapItems[0].location.x + h*(width + sfTool.horizontalGap)
                    objCopy.location.z = splitFlapItems[0].location.z - v*(height + sfTool.horizontalGap)
                    splitFlapItems.append(objCopy)
                    d += 1
            
            collIndex = 0
            while collIndex < 100:
                if "%sSystem%d" % (sfTool.identPrefix, collIndex) not in bpy.data.collections:
                    break
                collIndex += 1
            collName = "%sSystem%d" % (sfTool.identPrefix, collIndex)
            collection = bpy.data.collections.new(collName)
            collection["SplitFlapSettings.flapTime"] = sfTool.flapTime
            collection["SplitFlapSettings.characters"] = sfTool.characters
            collection["SplitFlap"] = self.collectionMarker
            bpy.context.scene.collection.children.link(collection)
            for splitFlapItem in splitFlapItems:
                collection.objects.link(splitFlapItem)
                if splitFlapItem == splitFlapItems[0]: #unlink original
                    otherCollections = [collection.name for collection in splitFlapItem.users_collection if collection.name != collName]
                    for otherCollName in otherCollections:
                        if otherCollName == "Scene Collection":
                            bpy.context.scene.collection.objects.unlink(splitFlapItem) 
                        else:
                            bpy.data.collections[otherCollName].objects.unlink(splitFlapItem)
        return {'FINISHED'}

def duplicateObject(obj, data=True, actions=True, collection=None):
    objCopy = obj.copy()
    if data:
        objCopy.data = objCopy.data.copy()
    if actions and objCopy.animation_data:
        objCopy.animation_data.action = objCopy.animation_data.action.copy()
    if collection is not None:
        collection.objects.link(objCopy)
    return objCopy