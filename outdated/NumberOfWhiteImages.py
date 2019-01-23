import os
root = "C:\Bachelor Workspace\dziFolder\H281-03\H281_files\\"
allTheFolders = [10,11, 12, 13, 14, 15, 16, 17, 18, 19]
filesFound = 0
for folder in allTheFolders:
    directory = os.fsencode(root + str(folder))
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".jpeg"):
            fileAndPath = os.fsdecode(root + "\\" + str(folder) +  "\\" + filename)
            if os.path.getsize(fileAndPath) < 1900: # Somewhat arbitrary, but choosen after looing at file sizes 
                print("File found: " + str(folder) + "\\" + filename + ". The size was: " + str(os.path.getsize(fileAndPath)) + ". Total files found: " + str(filesFound))
                filesFound = filesFound + 1
                continue
        else:
            continue

print("In the end, " + str(filesFound) + " files was found.")