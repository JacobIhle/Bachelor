import os
import glob

def RefreshImageList():
    try:
        listOfImages = glob.glob("//home/prosjekt/**/*.scn", recursive=True)
        with open('ImageList.txt', 'w') as f:
            for item in listOfImages:
                f.write("%s\n" % item)
    except OSError:
        return [], "500"

    return imageListToDict(listOfImages), ""


def ReadImageListFromFile():
    #TODO
    #write paths to dict with key = filename, value = path  DONE
    if os.path.isfile("./ImageList.txt"):
        try:
            with open("ImageList.txt") as f:
                listOfImages = f.read().splitlines()
        except OSError:
            return [], "500"

        return imageListToDict(listOfImages[0]), ""
    else:
        open("ImageList.txt", "w")
        return [], ""


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
        path = path[2:]
        BuildNestedHelper(path, path, container)
    return container




def RecursiveFuck(dict, returnString):
    for key, value in dict.items():
        if type(value) is list:
            returnString.append("<div class='folder'>\n")
            returnString.append("<button class='folderButtons'>"+key+"</button>\n")
            for image in value:
                returnString.append("<button class='imageLinks' id="+image+">"+image+"</button>\n")
            returnString.append("</div>\n")
        else:
            returnString.append("<div class='folder'>\n")
            returnString.append("<button class='folderButtons'>" + key + "</button>\n")
            RecursiveFuck(value, returnString)
            returnString.append("</div>\n")
    return


def CallFromJinja(availableImages):
    returnString = []
    RecursiveFuck(availableImages, returnString)
    return "".join(returnString)
