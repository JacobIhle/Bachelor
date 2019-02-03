import os
root = "C:\Bachelor Workspace\dziFolder\H281test\H281_files\\"
allTheFolders = [11, 12, 13, 14, 15, 16, 17, 18, 19]
filesRemoved = 0
for folder in allTheFolders:
    directory = os.fsencode(root + str(folder))
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".jpeg"):
            fileAndPath = os.fsdecode(root + "\\" + str(folder) +  "\\" + filename)
            if os.path.getsize(fileAndPath) < 1900: # Somewhat arbitrary, but choosen after looing at file sizes 
                print("File removed: " + str(fileAndPath) + ". The size was: " + str(os.path.getsize(fileAndPath)) + ". Files removed: " + str(filesRemoved))
                os.remove(fileAndPath)
                filesRemoved = filesRemoved + 1
                continue
        else:
            continue