import openslide
from openslide import deepzoom, open_slide
from openslide import OpenSlide
from flask import Flask, send_file, make_response, render_template
from optparse import OptionParser
import PIL
from PIL import Image
app = Flask(__name__)
path = "H281.scn"
image = openslide.OpenSlide(path)

images = image.associated_images
#thumbnail = image.get_thumbnail((10000,10000))
deepzom = deepzoom.DeepZoomGenerator(image)
print(deepzom.get_dzi("jpeg"))
rgb = deepzom.get_tile(10, (0,0))
region = image.read_region((20000, 110000), 0, (1500, 1500))
testregion = image.read_region((57000,110000), 0, (1000, 1000))
testregion.save("../Bachelor/testregion.png")
testregion.show()
#thumbnail.show()
print(image.dimensions)







