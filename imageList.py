import os
import glob

def RefreshImageList():
    try:
        listOfImages = glob.glob("//home/prosjekt/**/*.scn", recursive=True)
        strippedListOfImages = stripBeginningOfPaths(listOfImages)
        with open('ImageList.txt', 'w') as f:
            for item in strippedListOfImages:
                f.write("%s\n" % item)
    except OSError:
        return [], "500"

    return imageListToDict(strippedListOfImages), ""


def ReadImageListFromFile():
    if os.path.isfile("./ImageList.txt"):
        try:
            with open("ImageList.txt") as f:
                strippedListOfImages = f.read().splitlines()
        except OSError:
            return [], "500"

        return imageListToDict(strippedListOfImages), ""
    else:
        open("ImageList.txt", "w")
        return [], ""


def stripBeginningOfPaths(list):
    foo = []
    for element in list:
         foo.append(element.replace("//home/prosjekt", ""))
    return foo



def imageListToDict(list):
    result = {}
    for element in list:
        image = element.split("/")[-1]
        result[image] = element
    return result



def BuildNestedHelper(path, text, container):
    segs = path.split('/')
    head = segs[0]
    tail = segs[1:]
    tailtail = segs[2:]
    if not tailtail:
        if head not in container:
            container[head] = []
        container[head].append(tail[0])
    elif not tail:
        container[head] = text
    else:
        if head not in container:
            container[head] = {}
        BuildNestedHelper('/'.join(tail), text, container[head])


def BuildNested(paths):
    #TODO
    #paths will according to plan be converted to a dict DONE
    container = {}
    for key, path in paths.items():
        path = path[1:]
        BuildNestedHelper(path, path, container)
    return container




def BuildImageListHTML(dict, returnString, level):
    for key, value in dict.items():
        if type(value) is list:
            returnString.append("<div class='folder'>\n")
            returnString.append("<button class='folderButtons'>"+key+"</button>\n")
            for image in value:
                returnString.append("<button class='imageLinks' id="+image+">"+image+"</button>\n")
            returnString.append("</div>\n")
        elif level is 0:
            returnString.append("<div class='topFolders'>\n")
            returnString.append("<button class='folderButtons'>" + key + "</button>\n")
            BuildImageListHTML(value, returnString, level+1)
            returnString.append("</div>\n")
        else:
            returnString.append("<div class='folder'>\n")
            returnString.append("<button class='folderButtons'>" + key + "</button>\n")
            BuildImageListHTML(value, returnString, level+1)
            returnString.append("</div>\n")
    return


def GetImageListHTML(availableImages):
    returnString = []
    BuildImageListHTML(availableImages, returnString, 0)
    return "".join(returnString)
