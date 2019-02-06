#LICENSE: https://github.com/openslide/openslide/blob/master/lgpl-2.1.txt


from flask import Flask, send_file, render_template
import openslide
from openslide.deepzoom import DeepZoomGenerator
from io import BytesIO
import os

image = None
deepZoomGen = None
allAvailableImages = {}
app = Flask(__name__)



@app.route('/')
def Main():
    AvailableImages = GetAvailableImages()
    return render_template("index.html", images=AvailableImages)



@app.route('/images/<filename>')
def LoadControlImages(filename):
    return send_file("static/images/"+filename)


@app.route('/<year>/<filename>')
def changeImage(year, filename):
    global image; global deepZoomGen
    #TODO
    #add check for blank return string
    filename = FindFilenameFromList(year, filename)
    path = "../../../../prosjekt/Histology/bladder_cancer_images/"+year+"/"+filename
    image = openslide.OpenSlide(path)
    deepZoomGen = DeepZoomGenerator(image, tile_size=254, overlap=1, limit_bounds=False)
    return deepZoomGen.get_dzi("jpeg")


@app.route('/<year>/<dummyVariable>/<level>/<tile>')
def GetTile(year, dummyVariable, level, tile):
    col, row = GetNumericTileCoordinatesFromString(tile)
    img = deepZoomGen.get_tile(int(level), (int(col), int(row)))
    return serve_pil_image(img)


@app.route('/<root>/<imageID>/<file>')
def GetDzi(root, imageID, file):
    return send_file(root+"/"+imageID+"/"+file)


def FindFilenameFromList(year, filename):
    fileList = allAvailableImages[year]
    for file in fileList:
        if filename in file:
            return file
    return ""


#TODO
#FOR RUNNING ON UNIX SERVER

def GetAvailableImages():
    global allAvailableImages
    temp = {}
    for folderName1 in os.listdir("../../../../prosjekt/Histology/"):
        for folderName in os.listdir("../../../../prosjekt/Histology/"+folderName1):
            if os.path.isdir("../../../../prosjekt/Histology/"+folderName1+"/"+folderName):
                listOfFiles = []
                for filename in os.listdir("../../../../prosjekt/Histology/"+folderName1+"/"+folderName):
                    if ".scn" in filename:
                        listOfFiles.append(filename)
                if listOfFiles:
                    temp[folderName] = listOfFiles
        if temp:
            allAvailableImages[folderName1] = temp
    return allAvailableImages
'''

#TODO
#FOR TESTING PURPOSES
def GetAvailableImages():
    global allAvailableImages
    allAvailableImages = {"2002": ["1 6565.scn", "2 7658.scn", "3 23425.scn"],
                              "2003": ["1 25436.scn", "225.scn"],
                              "2004": ["125.scn"],
                              "2005": ["1.scn", "2.scn", "3 24536.scn", "4.scn", "5.scn", "6.scn"]
                              }
    return allAvailableImages
'''


def GetNumericTileCoordinatesFromString(tile):
    col, row = str.split(tile, "_")
    row = str.replace(row, ".jpeg", "")
    return col, row


def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=80)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, threaded=True)






