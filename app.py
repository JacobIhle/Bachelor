#LICENSE: https://github.com/openslide/openslide/blob/master/lgpl-2.1.txt


from flask import Flask, send_file, render_template
import openslide
from openslide.deepzoom import DeepZoomGenerator
from io import BytesIO

image = None
deepZoomGen = None

app = Flask(__name__)



@app.route('/')
def Main():
    return render_template("index.html")



@app.route('/images/<filename>')
def LoadControlImages(filename):
    return send_file("static/images/"+filename)


@app.route('/<year>/<filename>')
def changeImage(year, filename):
    global image; global deepZoomGen
    path = "../../../../prosjekt/Histology/bladder_cancer_images/"+year+"/"+str.replace(filename, "%", " ")+".scn"
    print(path)
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

@app.route('/PopulateImageExplorer')
def PopulateImageExplorer():
    return ""

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






