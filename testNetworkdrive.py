import os
import paramiko
from paramiko import client
import openslide
from openslide.deepzoom import DeepZoomGenerator
from PIL import Image

client = paramiko.client.SSHClient()
client.load_system_host_keys()
client.connect(hostname="ba5.ux.uis.no", port=22, username="thomaso", password="t4d4reve")
stftp = client.open_sftp()
file = stftp.open("/../../../home/prosjekt/Histology/bladder_cancer_images/2002/H10295-02 E_2013-07-09 11_06_26.scn")
stdin, stdout, stderr = client.exec_command('ls -l')
print(stdin)
print(file)

image = openslide.OpenSlide(file.read())
deepZoomGen = DeepZoomGenerator(image, tile_size=254, overlap=1, limit_bounds=False)
img = deepZoomGen.get_tile(19, 650, 140)
img.show()