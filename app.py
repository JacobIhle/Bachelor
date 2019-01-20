from flask import Flask, send_file, render_template
import openslide
from openslide.deepzoom import DeepZoomGenerator
from tempfile import NamedTemporaryFile
from shutil import copyfileobj
from os import remove

image = None
deepZoomGen = None

app = Flask(__name__)


@app.route('/')
def Main():
    return render_template("index.html")


@app.route('/scnImages/<filename>')
def changeImage(filename):
    global image; global deepZoomGen
    image = openslide.OpenSlide("scnImages/"+filename+".scn")
    deepZoomGen = DeepZoomGenerator(image, tile_size=254, overlap=1, limit_bounds=False)
    return deepZoomGen.get_dzi("jpeg")


@app.route('/scnImages/<dummyVariable>/<level>/<tile>')
def GetTile(dummyVariable ,level, tile):
    col, row = GetNumericTileCoordinatesFromString(tile)
    tileImage = TileCoordinatesToJpegImage(level, col, row)
    response = send_file(tileImage, mimetype="image/jpeg")
    return response


@app.route('/<root>/<imageID>/<file>')
def GetDzi(root, imageID, file):
    return send_file(root+"/"+imageID+"/"+file)


def GetNumericTileCoordinatesFromString(tile):
    col, row = str.split(tile, "_")
    row = str.replace(row, ".jpeg", "")
    return col, row


def TileCoordinatesToJpegImage(level, col, row):
    jpegImage = NamedTemporaryFile(mode='w+b', suffix='jpg')
    deepZoomGen.get_tile(int(level), (int(col), int(row))).save("/tmp/myfile.jpg")

    pilImage = open('/tmp/myfile.jpg', 'rb')
    copyfileobj(pilImage, jpegImage)
    pilImage.close()

    remove('/tmp/myfile.jpg')
    jpegImage.seek(0, 0)
    return jpegImage


if __name__ == '__main__':
    app.run(port=5000)






