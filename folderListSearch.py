import os
import glob

print(glob.glob("//home/prosjekt/**/*.scn", recursive=True))


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
