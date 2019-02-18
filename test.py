import imageList

test = ["//home/prosjekt/test/fuuuuuuu/shit/dritt.scn", "//home/prosjekt/test/fuuuuuuu/shit/ass.scn"]
foo = imageList.stripBeginningOfPaths(test)
print(imageList.imageListToDict(foo))
