import pyvips
from pyvips import Image



test = Image.new_from_file("dz_files/11/1_1.jpeg")
test = test.draw_line([0, 255, 0], 0, 0, 100000, 110000)

test.pngsave("testy.png")





