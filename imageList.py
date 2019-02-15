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

    return listOfImages, ""


def ReadImageListFromFile():
    if os.path.isfile("./ImageList.txt"):
        try:
            with open("ImageList.txt") as f:
                listOfImages = f.read().splitlines()
        except OSError:
            return [], "500"

        return listOfImages, ""
    else:
        open("ImageList.txt", "w")
        return [], ""


def build_nested_helper(path, text, container):
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
        build_nested_helper('/'.join(tail), text, container[head])


def build_nested(paths):
    container = {}
    for path in paths:
        path = path[2:]
        build_nested_helper(path, path, container)
    return container


def msg(path):
    return path.lower()