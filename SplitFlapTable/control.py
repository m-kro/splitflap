# Copyright (c) 2023, Mirko Barthauer
# All rights reserved.

# This source code is licensed under the MIT-style license found in the
# LICENSE file in the same directory of this source tree.

import os
import bpy
import math
import addon_utils
from mathutils import Vector

from .texture import createCharactersTexture, findFont
from .structures import SplitFlapKeySettings, SplitFlapSettings, flapKeySettings_updateTextSource, flapAnimation_updateDisplay

class SplitFlapPanel(bpy.types.Panel):
    bl_label = "SplitFlap Panel"
    bl_idname = "OBJECT_PT_SplitFlapPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type= "UI"
    bl_category = "Split Flap"
    
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
        row.prop(sfTool, "charWidth")
        row.prop(sfTool, "charHeight")
        row.prop(sfTool, "flapRatio")
        row = layout.row()
        row.prop(sfTool, "fontName")
        row = layout.row()
        row.prop(sfTool, "identPrefix")
        row = layout.row()
        row.prop(sfTool, "fontColor")
        row = layout.row()
        row.prop(sfTool, "backgroundColor")
        row = layout.row()
        row.prop(sfTool, "createFrame")
        row = layout.row()
        row.operator("object.splitflapcontroller", text="Create split flap items")


class SplitFlapAnimationPanel(bpy.types.Panel):
    bl_label = "SplitFlapAnimation Panel"
    bl_idname = "OBJECT_PT_SplitFlapAnimationPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type= "UI"
    bl_category = "Split Flap"

    def draw(self, context):
        layout = self.layout
        sfKeySetting = context.scene.splitFlapKeySetting
        textStatus = context.scene.textStatusMessage
        row = layout.row()
        row.template_list("OBJECT_UL_SplitFlapAnimationListItem", "", bpy.context.scene.splitFlapAnimations, "items", 
                            bpy.context.scene, "splitFlapAnimationIndex", rows=2, maxrows=5, type='DEFAULT')
        row = layout.row()
        row.prop(sfKeySetting, "useTextInput")
        if sfKeySetting.useTextInput:
            row.prop(sfKeySetting, "text")
        else:
            row.prop(sfKeySetting, "textBlock", expand=True)
        if len(textStatus) > 0:
            row = layout.row()
            layout.label(text=textStatus)
        row = layout.row()
        row.prop(sfKeySetting, "keyTime")
        row = layout.row()
        row.prop(sfKeySetting, "extend")
        row.prop(sfKeySetting, "center")
        row = layout.row()
        row.prop(sfKeySetting, "collection", expand=True)
        row = layout.row()
        row.operator("object.splitflapanimationcontroller", text="add entry").action='ADD'
        row.operator("object.splitflapanimationcontroller", text="update entry").action='UPDATE'
        row.operator("object.splitflapanimationcontroller", text="remove entry").action='DELETE'
        row = layout.row()
        row.operator("object.splitflapapplyframes")

class SplitFlapAnimationListItem(bpy.types.UIList):
    bl_label = "SplitFlapAnimation List Item"
    bl_idname = "OBJECT_UL_SplitFlapAnimationListItem"

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text="%s (%s t %.2f)" % (item.text, item.collectionID, item.keyTime))
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="")

class SplitFlapAnimationList(bpy.types.PropertyGroup):
    itemIndex : bpy.props.IntProperty(name="itemIndex", default=0)
    items : bpy.props.CollectionProperty(name="items", type=SplitFlapKeySettings)

class SplitFlapAnimationController(bpy.types.Operator):
    bl_idname = "object.splitflapanimationcontroller"
    bl_label = "Add Split Flap Animation"
    action: bpy.props.EnumProperty(
        items=[
            ('DELETE', 'remove entry', 'remove entry'),
            ('UPDATE', 'update entry', 'update entry'),
            ('ADD', 'add entry', 'add entry')
        ]
    )
    
    def execute(self, context):
        sfKeySetting = context.scene.splitFlapKeySetting
        sfAnimations = context.scene.splitFlapAnimations
        
        # update text (text input can remain the same but contain new text)
        flapKeySettings_updateTextSource(sfKeySetting, context)
        print(sfKeySetting) # TODO
        
        # checks
        if len(sfKeySetting.collectionID) == 0:
            self.report({'INFO'}, "Please choose a collection of split flap items to animate!")
            return {'FINISHED'}
        
        if self.action == "ADD" or self.action == "UPDATE":
            # convert the string according to the available characters
            characters = bpy.data.collections[sfKeySetting.collectionID]["SplitFlapSettings.characters"]
            newText = self.formatText(sfKeySetting.text, context)
            sfKeySetting.formattedText = newText
            
            timeDiffPrev = self.feasibleTime(context, deltaIndex = -1)
            timeDiffNext = self.feasibleTime(context, deltaIndex = 1)
            if timeDiffPrev < 0:
                self.report({'INFO'}, "The time is not sufficient to flap from the previous text. The time diff. amounts to %.2f s." % timeDiffPrev)
                return {'FINISHED'}
            elif timeDiffNext < 0:
                self.report({'INFO'}, "The time is not sufficient to flap to the next text. The time diff. amounts to %.2f s." % timeDiffNext)
                return {'FINISHED'}
            elif len(sfKeySetting.collectionID) > 0 and sfKeySetting.collectionID in bpy.data.collections:
                # check if there is already an entry for the same time
                frameSettings = [frame for frame in sfAnimations.items if frame.collectionID == sfKeySetting.collectionID and abs(frame.keyTime - sfKeySetting.keyTime) < 0.1]
                done = False
                if self.action == "UPDATE":
                    index = context.scene.splitFlapAnimationIndex
                    item = sfAnimations.items[index]
                    item.text = sfKeySetting.text
                    item.formattedText = sfKeySetting.formattedText
                    item.extend = sfKeySetting.extend
                    item.keyTime = sfKeySetting.keyTime
                    item.center = sfKeySetting.center
                    done = True
                elif len(frameSettings) == 0:
                    item = sfAnimations.items.add()
                    sfAnimations.itemIndex = len(sfAnimations.items) - 1
                    item.text = sfKeySetting.text
                    item.formattedText = sfKeySetting.formattedText
                    item.keyTime = sfKeySetting.keyTime
                    item.extend = sfKeySetting.extend
                    item.center = sfKeySetting.center
                    item.collectionID = sfKeySetting.collectionID
                    done = True
                if not done:
                    self.report({'INFO'}, "The item could not be added/updated due to missing input or duplicated data.")
        elif self.action == "DELETE":
            index = context.scene.splitFlapAnimationIndex
            if index >= 0:
                sfAnimations.items.remove(index)
                context.scene.splitFlapAnimationIndex -= 1
        return {'FINISHED'}
    
    def formatText(self, text, context):
        sfKeySetting = context.scene.splitFlapKeySetting
        colCount = sfKeySetting.collection["SplitFlapSettings.colCount"]
        characters = sfKeySetting.collection["SplitFlapSettings.characters"]
        text = text.replace("\r", "")
        if "\n" in text:
            print("newline in text")
            if colCount is None or ' ' not in characters:
                text = text.replace("\n", "")
            elif colCount is not None: # fill incomplete lines with space characters
                print("Fill with space characters")
                idx = 0
                while idx < len(text):
                    nextNewLine = text.find("\n")
                    if nextNewLine < 0:
                        break
                    diffToFullRow = colCount - nextNewLine % colCount
                    text = text.replace("\n", ' ' * diffToFullRow, 1)
                    print("Inserted %d space characters to fill the line" % diffToFullRow)
                    idx = nextNewLine + diffToFullRow
        print("format '%s'" % text)
        newTextList = []
        for char in text:
            if char in characters:
                newTextList.append(char)
            elif char.lower() in characters:
                newTextList.append(char.lower())
            elif char.upper() in characters:
                newTextList.append(char.upper())
            elif char in ("\n", "\r"):
                continue
            elif ' ' in characters:
                newTextList.append(' ')
        print("formatted string: %s" % ("".join(newTextList)))
        return "".join(newTextList)
    
    def feasibleTime(self, context, deltaIndex = -1):
        sfKeySetting = context.scene.splitFlapKeySetting
        sfAnimations = context.scene.splitFlapAnimations
        if len(sfAnimations.items) == 0:
            return 0
            
        # get time and text to add
        index = context.scene.splitFlapAnimationIndex
        collection = bpy.data.collections[sfAnimations.items[index].collectionID]
        flapTime = collection["SplitFlapSettings.flapTime"]
        characters = collection["SplitFlapSettings.characters"]
        
        size = len(sfAnimations.items)
        for i in range(size):
            if len(sfAnimations.items[i].formattedText) == 0:
                sfAnimations.items[i].formattedText = self.formatText(sfAnimations.items[i].text, context)
        
        flapCount = len(collection.objects)
        frames = [(item.keyTime, item.formattedText, False) for item in sfAnimations.items]
        if self.action == "UPDATE":
            frames[index] = (sfKeySetting.keyTime, sfKeySetting.formattedText, True)
        else:
            frames.append((sfKeySetting.keyTime, sfKeySetting.text, True))
        # check if the time difference is enough to switch to the new text
        frames.sort(key=lambda x:x[0])
        newIndex = -1
        for i in range(len(frames)):
            if frames[i][2]:
                newIndex = i
                break
        if deltaIndex < 0: # check previous
            #print("newIndex %d text %s frames %s" % (newIndex, sfKeySetting.text, str(frames)))
            if newIndex > 0: 
                deltaT = frames[newIndex][0] - frames[newIndex-1][0]
                newString = self.__getFinalString(flapCount, sfAnimations.items, newIndex, sfKeySetting)
                previousString = self.__getFinalString(flapCount, sfAnimations.items, newIndex-1, sfKeySetting)
                #print("characters %s newString %s" % (characters, newString))
                neededTime = max([self.__getFlaps(entry[0], entry[1], characters) for entry in zip(previousString, newString)]) * flapTime
                return deltaT - neededTime
            else:
                if frames[newIndex][0] < 0.01:
                    return 0
                else:
                    fromString = "A" * flapCount
                    newString = self.__getFinalString(flapCount, sfAnimations.items, newIndex, sfKeySetting)
                    neededTime = max([self.__getFlaps(entry[0], entry[1], characters) for entry in zip(fromString, newString)]) * flapTime
                    return frames[newIndex][0] - neededTime
        else: # check next
            if newIndex > len(sfAnimations.items) - 2:
                return 0
            else:
                deltaT = frames[newIndex+1][0] - frames[newIndex][0]
                nextString = self.__getFinalString(flapCount, sfAnimations.items, newIndex+1, sfKeySetting)
                newString = self.__getFinalString(flapCount, sfAnimations.items, newIndex, sfKeySetting)
                neededTime = max([self.__getFlaps(entry[0], entry[1], characters) for entry in zip(newString, nextString)]) * flapTime
                return deltaT - neededTime
    
    def __getFinalString(self, length, items, index, newItem):
        if newItem is None:
            newItem = items[index]
        textLen = len(newItem.formattedText)
        if textLen >= length:
            return newItem.formattedText[:length]
        if newItem.center:
            indent = (length - textLen)//2
            remainder = length - indent - textLen
            return " " * indent + newItem.formattedText + " " * remainder
        elif newItem.extend:
            remainder = length - textLen
            return newItem.formattedText + " " * remainder
        else:
            previousString = self.__getFinalString(length, items, index-1, None)
            return newItem.formattedText + previousString[textLen:]
    
    def __getFlaps(self, fromChar, toChar, characters):
        print("from %s to %s in %s" % (fromChar, toChar, characters))
        startIndex = characters.index(fromChar)
        targetIndex = characters.index(toChar)
        return targetIndex - startIndex if targetIndex >= startIndex else len(characters) - startIndex + targetIndex

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
                i = 0
                if frameSetting.extend:
                    targetString = frameSetting.formattedText[:maxLen] if len(frameSetting.formattedText) >= maxLen else frameSetting.formattedText + " " * (maxLen - len(frameSetting.formattedText))
                elif frameSetting.center:
                    textLen = len(frameSetting.formattedText)
                    if textLen >= maxLen:
                        targetString = frameSetting.formattedText[:maxLen]
                    else:
                        indent = (maxLen - textLen)//2
                        remainder = maxLen - indent - textLen
                        targetString = " " * indent + frameSetting.formattedText + " " * remainder
                else:
                    targetString = "%s%s" % (frameSetting.formattedText[:maxLen], lastString[len(frameSetting.formattedText):])
                startFrame = int(round(fps * frameSetting.keyTime))
                print("lastString '%s' targetString '%s'" % (lastString, targetString))
                
                for obj in coll.all_objects:
                    if not "SplitFlapItem" in obj:
                        print("skip obj %s" % obj.name)
                        continue
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
        context.scene.frame_set(frameBefore) # set frame back to begin
        return {'FINISHED'}


class SplitFlapController(bpy.types.Operator):
    bl_idname = "object.splitflapcontroller"
    bl_label = "Split Flap Controller"
    #bl_options = {'REGISTER', 'UNDO'}
    
    # template for split flaps
    templatePath : bpy.props.StringProperty(default='')
    templateFile : bpy.props.StringProperty(default="splitFlapTemplate.blend")
    innerPath = "Object"
    cardName = "CardExample"
    itemName = "SplitFlapItem"
    materialName = "Mat.Flapcard"
    frameMaterialName = "BlackMetal"
    collectionMarker = "SplitFlap"
    uvAttribute = "MyUVMap"
    charSpace = (120,200)
    
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
        templateFlapItem = None if len(context.scene.splitFlapTemplate) == 0 or context.scene.splitFlapTemplate not in bpy.data.objects else bpy.data.objects[context.scene.splitFlapTemplate]
        cardTemplate = None if len(context.scene.cardTemplate) == 0 or context.scene.cardTemplate not in bpy.data.objects else bpy.data.objects[context.scene.cardTemplate]
        if templateFlapItem is None or cardTemplate is None:
            for material in bpy.data.materials: # search for orphan material data which disturbs the fresh import
                if (material.name.startswith(self.materialName) or material.name.startswith(self.frameMaterialName)) and not material.users:
                    print("Remove unused material %s" % material.name)
                    bpy.data.materials.remove(material)
            bpy.ops.wm.append(
                filepath=os.path.join(self.templatePath, self.innerPath, self.itemName),
                directory=os.path.join(self.templatePath, self.innerPath),
                filename=self.itemName
            )
            bpy.context.view_layer.update()
            
            # import material too
            with bpy.data.libraries.load(self.templatePath) as (dataFrom, dataTo):
                dataTo.materials = dataFrom.materials
            # pass the current SplitFlapProperties to Geometry Nodes input where necessary
            newObjectNames = [obj.name for obj in context.scene.objects if obj.name not in oldObjectNames and obj.name.startswith(self.itemName)]
            newCardNames = [obj.name for obj in context.scene.objects if obj.name not in oldObjectNames and obj.name.startswith(self.cardName)]
            
            if len(newObjectNames) > 0 and len(newCardNames) > 0:
                context.scene.splitFlapTemplate = newObjectNames[0]
                context.scene.cardTemplate = newCardNames[0]
                templateFlapItem = bpy.data.objects[context.scene.splitFlapTemplate]
                cardTemplate = bpy.data.objects[context.scene.cardTemplate]
                print("imported cardTemplate object name: '%s'" % newCardNames[0])
            else:
                self.report({'ERROR'}, "The import of the flap item template failed.")
                return {'FINISHED'}
        
        sfTool = context.scene.splitFlapTool
        # generate texture
        fontPath = findFont(sfTool.fontName)
        texturePath = None
        textureFile = "FlapCharacters%d.png"
        
        if fontPath is None:
            self.report({'ERROR'}, "The font %s could not be found or cannot be used as a TrueType font." % sfTool.fontName)
            return {'FINISHED'}
        
        # generate texture
        textureIndex = 0
        while os.path.exists(os.path.join(bpy.path.abspath("//"), textureFile % textureIndex)):
            textureIndex += 1
        textureFile = textureFile % textureIndex
        texturePath = os.path.join(bpy.path.abspath("//"), textureFile)
        fontColor = [min(255, int(255*round(value))) for value in [sfTool.fontColor.r, sfTool.fontColor.g, sfTool.fontColor.b]]
        fontColor.append(255)
        backgroundColor = [min(255, int(255*round(value))) for value in [sfTool.backgroundColor.r, sfTool.backgroundColor.g, sfTool.backgroundColor.b]]
        backgroundColor.append(255)
        charsPerRow = math.ceil(math.sqrt(len(sfTool.characters)))
        defaultTextureRatio = self.charSpace[0] / self.charSpace[1]
        createCharactersTexture(charSpace=(self.charSpace[0], int(self.charSpace[1] * defaultTextureRatio / sfTool.flapRatio)), characters=sfTool.characters, 
                                fontPath=fontPath, output=texturePath, color=tuple(fontColor), background=tuple(backgroundColor),
                                fontFactorWidth=sfTool.charWidth, fontFactorHeight=sfTool.charHeight, itemsPerSide=charsPerRow)
        splitFlapItems = []
        prefix = '' if " " in sfTool.identPrefix else sfTool.identPrefix
        newCard = duplicateObject(cardTemplate)
        newCard.hide_render = True
        cardTemplate.hide_viewport = True
        cardTemplate.hide_render = True
        newMat = None
        oldMat = bpy.data.materials.get(self.materialName)
        if oldMat is not None:
            newMat = oldMat.copy()
            newMat.node_tree.nodes["Image Texture"].image = bpy.data.images.load("//%s" % textureFile)
            for slot in newCard.material_slots:
                if slot.material.name.startswith(self.materialName):
                    print("replace material %s with new one in card" % slot.material.name)
                    slot.material = newMat
                    break
        newObj = duplicateObject(templateFlapItem)
        for slot in newObj.material_slots:
            if slot.material.name.startswith(self.materialName):
                print("replace material %s with new one in flapItem" % slot.material.name)
                slot.material = newMat
                break
        templateFlapItem.hide_viewport = True
        templateFlapItem.hide_render = True
        newObj.hide_viewport = False
        newObj.hide_render = False

        for modifier in newObj.modifiers:
            if modifier.type == 'NODES' and modifier.name == "SplitFlapCircle":
                modifier["Input_3"] = sfTool.flapRadius
                modifier["Input_4"] = sfTool.characters
                modifier["Input_5"] = charsPerRow
                modifier["Input_7"] = charsPerRow
                modifier["Input_8"] = 0.
                modifier["Input_9"] = newCard
                modifier["Output_6_attribute_name"] = self.uvAttribute
                # rename object according to the wanted prefix
                newObj.name = "%sItem0" % prefix
        #unlink original
        otherCollections = [collection.name for collection in newObj.users_collection if collection.name != collName]
        for otherCollName in otherCollections:
            if otherCollName == "Scene Collection":
                bpy.context.scene.collection.objects.unlink(newObj) 
            else:
                bpy.data.collections[otherCollName].objects.unlink(newObj)
        newObj["SplitFlapItem"] = True
        splitFlapItems.append(newObj)
        
        # Create the collection
        collIndex = 0
        while collIndex < 200:
            if "%sSystem%d" % (sfTool.identPrefix, collIndex) not in bpy.data.collections:
                break
            collIndex += 1
        collName = "%sSystem%d" % (sfTool.identPrefix, collIndex)
        collection = bpy.data.collections.new(collName)
        collection["SplitFlapSettings.flapTime"] = sfTool.flapTime
        collection["SplitFlapSettings.characters"] = sfTool.characters
        collection["SplitFlapSettings.rowCount"] = sfTool.rowCount
        collection["SplitFlapSettings.colCount"] = sfTool.colCount
        collection["SplitFlap"] = self.collectionMarker
        bpy.context.scene.collection.children.link(collection)
        newCard.name = "%sCard%d" % (sfTool.identPrefix, collIndex)
        collection.objects.link(newCard)
        
        # optionally scale the flap item, maintain the current width
        newCard.scale.z = newCard.dimensions[0]*newCard.scale.x/(2*newCard.dimensions[2]*sfTool.flapRatio)
        newCard.hide_viewport = False
        applyTransforms(context, [newCard], location=False, rotation=False, scale=True)
        newCard.hide_viewport = True
        
        # make the wanted number of copies and add them to the same collection
        # get width and height of the split flap item
        splitFlapItems[0].name = "%sItem%d.%d" % (sfTool.identPrefix, collIndex, 0)
        d = 1
        collection.objects.link(splitFlapItems[0])
        bpy.context.view_layer.update()
        width = splitFlapItems[0].dimensions.x
        height = splitFlapItems[0].dimensions.z
        print("splitFlapItem height %.2f" % height)
        bounds = []
        bounds.append(splitFlapItems[0].bound_box)
        
        for v in range(0, sfTool.rowCount):
            for h in range(0, sfTool.colCount):
                if h == 0 and v == 0:
                    
                    continue
                objCopy = duplicateObject(splitFlapItems[0])
                objCopy.name = "%sItem%d.%d" % (sfTool.identPrefix, collIndex, d)
                objCopy.location.x = splitFlapItems[0].location.x + h*(width + sfTool.horizontalGap)
                objCopy.location.z = splitFlapItems[0].location.z - v*(height + sfTool.verticalGap)
                splitFlapItems.append(objCopy)
                #print("split flap copy h=%d v=%d x0=%.2f z0=%.2f x=%.2f z=%.2f height=%.2f" % (h, v, splitFlapItems[0].location.x, splitFlapItems[0].location.z, objCopy.location.x, objCopy.location.z, height))
                d += 1
        
        for splitFlapItem in splitFlapItems[1:]:
            bounds.append(splitFlapItem.bound_box)
            collection.objects.link(splitFlapItem)
        
        # optionally create the frame mesh / cut out holes for the flap items
        if sfTool.createFrame:
            bpy.context.view_layer.update()
            locBegin = getBoundingBoxCenter(splitFlapItems[0])
            locEnd = getBoundingBoxCenter(splitFlapItems[-1])
            dimensions = splitFlapItems[0].dimensions
            add = (0.1, 0.05, 0.1)
            factor = 0.5
            xMin = locBegin.x - (factor + add[0]) * dimensions.x 
            xMax = locEnd.x + (factor + add[0]) * dimensions.x
            yMin = locBegin.y - (factor + add[1]) * dimensions.y
            yMax = locEnd.y + (factor + add[1]) * dimensions.y
            zMin = locEnd.z - (factor + add[2]) * dimensions.z 
            zMax = locBegin.z + (factor + add[2]) * dimensions.z
            #print("X %.2f - %.2f\nY  %.2f - %.2f\nZ %.2f - %.2f" % (xMin, xMax, yMin, yMax, zMin, zMax))
            frameSize = (0.5 * abs(xMax-xMin), 0.5 * abs(yMax-yMin), 0.5 * abs(zMax-zMin))
            frameCenter = (0.5 * (xMin + xMax), 0.5 * (yMin + yMax), 0.5 * (zMin + zMax))
            bpy.ops.mesh.primitive_cube_add(location=frameCenter, scale=frameSize)
            frameObj = context.object
            
            # add cutters for the split flap items
            tempSelectedObj = bpy.context.view_layer.objects.active
            bpy.ops.object.select_all(action='DESELECT')
            cutters = []
            for splitFlapItem in splitFlapItems:
                loc = getBoundingBoxCenter(splitFlapItem)
                dim = splitFlapItem.dimensions
                loc.y -= 0.15*dim.y
                scaled = (dim.x*1.03*0.5, dim.y*1.1*0.5, dim.z*1.02*0.5)
                bpy.ops.mesh.primitive_cube_add(location=loc, scale=scaled)
                cutterObj = context.object
                cutters.append(cutterObj)
            # join cutter objects
            with bpy.context.temp_override(active_object=cutters[0], selected_editable_objects=cutters):
                bpy.ops.object.join()
            boolObj = cutters[0]
            boolModifier = frameObj.modifiers.new(type="BOOLEAN", name="cutFrame")
            boolModifier.object = boolObj
            boolModifier.operation = 'DIFFERENCE'
            bpy.context.view_layer.objects.active = frameObj
            bpy.ops.object.modifier_apply(modifier="cutFrame")
            bpy.ops.object.select_all(action='DESELECT')
            boolObj.select_set(True)
            bpy.ops.object.delete()
            frameObj.name = "%s_frame" % collName
            moveToCollection(frameObj, collection)
            # apply material
            frameMat = bpy.data.materials.get("BlackMetal")
            if frameMat is not None:
                if frameObj.data.materials:
                    frameObj.data.materials[0] = frameMat
                else:
                    frameObj.data.materials.append(frameMat)
            parent(context, splitFlapItems, frameObj)
            frameObj.location = context.scene.cursor.location # move frame to cursor
            
        # choose as default split flap items if there is no other selected
        sfKeySetting = context.scene.splitFlapKeySetting
        if sfKeySetting.collection is None:
            sfKeySetting.collection = collection
        return {'FINISHED'}

def parent(context, childrenList, parentObj):
    if len(bpy.context.selected_objects) > 0:
        bpy.ops.object.select_all(action="DESELECT")
    for child in childrenList:
        child.select_set(True)
    parentObj.select_set(True)
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
    bpy.ops.object.select_all(action="DESELECT")

def getBoundingBoxCenter(obj):
    localCenter = 0.125 * sum((Vector(b) for b in obj.bound_box), Vector())
    return obj.matrix_world @ localCenter

def moveToCollection(obj, collection, exclusive=True):
    if exclusive:
        for coll in obj.users_collection:
            coll.objects.unlink(obj)
    if obj.name not in collection.objects:
        collection.objects.link(obj)

def duplicateObject(obj, data=True, actions=True, collection=None):
    objCopy = obj.copy()
    if data:
        objCopy.data = objCopy.data.copy()
    if actions and objCopy.animation_data:
        objCopy.animation_data.action = objCopy.animation_data.action.copy()
    if collection is not None:
        collection.objects.link(objCopy)
    return objCopy
    
def applyTransforms(context, objList, location=True, rotation=True, scale=True):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objList:
        obj.select_set(True)
    bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale)
    for obj in objList:
        obj.select_set(False)
