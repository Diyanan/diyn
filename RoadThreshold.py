from PIL import Image
import os
def BinaryImage(imageFile,threshold_b = 127):
    print "start process..."
    im = Image.open(imageFile)
    lim = im.convert("L")
    table = []
    for i in range(256):
        if i<threshold_b:
            table.append(0)
        else:
            table.append(255)
    bim = lim.point(table,"1")
    dirname = os.path.dirname(imageFile)
    filename = os.path.basename(imageFile)
    outpath = dirname+"/Binary_"+filename
    bim.save(outpath)
    print "process over!"