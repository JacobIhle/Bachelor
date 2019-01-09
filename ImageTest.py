import openslide
from openslide import deepzoom, open_slide
from flask import Flask, send_file, make_response, render_template
from optparse import OptionParser
from PIL import Image
app = Flask(__name__)
path = "H281.scn"
image = openslide.OpenSlide(path)
images = image.associated_images
#thumbnail = image.get_thumbnail((10000,10000))
deepzom = deepzoom.DeepZoomGenerator(image)
rgb = deepzom.get_tile(10, (0,0))
region = image.read_region((20000, 110000), 0, (1500, 1500))
testregion = image.read_region((97000,200000), 0, (1000, 1000))
testregion.show()
#thumbnail.show()
print(image.dimensions)







