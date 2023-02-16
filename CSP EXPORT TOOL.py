# CSP MUST BE OPEN

import os
import time
import json
import pyautogui
import shutil

# CONSTANTS
cspExportFolder = "\\export"
timetableFolder = "\\"
frameRate = 24

nextTimelineHotkey = ["ctrl", "num7"]
exportSheetHotkey = ["ctrl", "num9"]
exportSequenceHotkey = ["ctrl", "num8"]

sortedSpriteFolder = "\\sprites"
spriteExtension = ".png"
godotResourcePath = "res://blademaster/characters/blademaster/sprites"
godotAnimationFileName = "Animations.tres"

# RUNTIME
animationCount = 0
animations = { }
reachedEnd = False

# CLASSES
class Track:
    frames = { }

    def __init__(self):
        self.frames = { }

class Animation:
    name = ""
    duration = 0
    tracks = { }

    def __init__(self):
        self.name = ""
        self.duration = 0
        self.tracks = { }

    def AllChangedFrames(self):
        changes = []
        for index in range(self.duration):
            for track in self.tracks.values():
                if index in track.frames:
                    changes.append(index)
                    break
        return changes

def ReadXDTS(name):
    global reachedEnd

    fileObj = open(os.path.dirname(__file__) + "\\" + timetableFolder + name + ".xdts")
    rawData = fileObj.read()
    jsonString = ''.join(rawData.splitlines(keepends=True)[1:])
    parsed = json.loads(jsonString)

    # Create animation
    newAnim = Animation()
    newAnim.name = parsed["timeTables"][0]["name"]
    newAnim.duration = parsed["timeTables"][0]["duration"]

    if newAnim.name in animations:  
        reachedEnd = True
        return

    # Get track names
    trackNames = parsed["timeTables"][0]["timeTableHeaders"][0]["names"]
    tracks = parsed["timeTables"][0]["fields"][0]["tracks"]

    for index in range(len(trackNames)):
        newTrack = ConstructTrack(tracks[index])
        newAnim.tracks[trackNames[index]] = newTrack
    
    animations[newAnim.name] = newAnim
    fileObj.close()
    
def ConstructTrack(trackData):
    newTrack = Track()
    for frame in trackData["frames"]:
        cel = frame["data"][0]["values"][0]
        if cel == "SYMBOL_NULL_CELL":
            continue

        newTrack.frames[frame["frame"]] = cel
    return newTrack

def ExportSheet():
    pyautogui.hotkey(*exportSheetHotkey)
    time.sleep(0.5)
    pyautogui.write(str(animationCount) + ".xdts")
    pyautogui.press("enter")
    pyautogui.press("left")
    pyautogui.press("enter")

def ExportSequence():
    pyautogui.hotkey(*exportSequenceHotkey)
    time.sleep(0.1)
    pyautogui.press("enter")
    time.sleep(0.1)
    pyautogui.press("enter")

def CreateGodotFile():
    loadSteps = 1
    
    extResourceData = ""
    resourceData = "[resource]\nanimations = [ "

    for anim in animations.values():
        resourceData += "{\n\"frames\": [ "

        changes = anim.AllChangedFrames()

        for frame in range(anim.duration):
            if frame in changes:
                extResourceData += "[ext_resource path=\"" + godotResourcePath + "/" + anim.name + "/" + anim.name + "_" + f"{frame:04}" + spriteExtension + "\" type=\"Texture\" id=" + str(loadSteps) + "]\n"
                loadSteps += 1
            resourceData += "ExtResource( " + str(loadSteps - 1) + " ), "
        
        resourceData = resourceData[:-2]
        resourceData += " ],\n\"loop\": true,\n\"name\": \"" + anim.name + "\",\n\"speed\": " + f"{frameRate:.1f}" + "\n}, "
    
    resourceData = resourceData[:-2]
    resourceData += " ]\n"

    assembledData = "[gd_resource type=\"SpriteFrames\" load_steps=" + str(loadSteps) + " format=2]\n\n"
    assembledData += extResourceData + "\n"
    assembledData += resourceData

    filePath = os.path.dirname(__file__) + sortedSpriteFolder + "\\" + godotAnimationFileName
    fileObj = open(filePath, "w")
    fileObj.write(assembledData)
    fileObj.close()
    print("Animation file written")

def CopySprites():
    for anim in animations.values():
        folder = os.path.dirname(__file__) + sortedSpriteFolder + "\\" + anim.name
        if not os.path.exists(folder):
            os.mkdir(folder)

        changes = anim.AllChangedFrames()

        for frame in changes:
            srcSpriteLoc = os.path.dirname(__file__) + cspExportFolder + "\\" + anim.name + "_" + f"{frame:04}" + spriteExtension
            shutil.copy(srcSpriteLoc, folder)

# MAIN
print("TOOL WILL START IN 3 SECONDS. FOCUS CSP NOW!")
time.sleep(3)
# pyautogui.PAUSE = 0.5

while reachedEnd is not True:
    ExportSequence()
    ExportSheet()
    ReadXDTS(str(animationCount))
    pyautogui.hotkey(*nextTimelineHotkey)

    # reachedEnd = True
    animationCount += 1

print("Animation export done! Creating animation file...")

CreateGodotFile()
CopySprites()
