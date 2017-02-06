# -*- coding: utf-8 -*-
import os
from PIL import Image
from RoadThreshold import BinaryImage


def splitimage(srclist, rownum, colnum, dstpath):
    for src in srclist:
        img = Image.open(src)
        w, h = img.size
        if rownum <= h and colnum <= w:
            print('Original image info: %sx%s, %s, %s' % (w, h, img.format, img.mode))
            print('Start splitting images,please wait...')

            s = os.path.split(src)
            if dstpath == '':
                dstpath = s[0]
            fn = s[1].split('.')
            basename = fn[0]
            ext = fn[-1]

            num = 0
            rowheight = h // rownum
            colwidth = w // colnum
            for r in range(rownum):
                for c in range(colnum):
                    box = (c * colwidth, r * rowheight, (c + 1) * colwidth, (r + 1) * rowheight)
                    if c == colnum-1:
                        img.crop(box).save(os.path.join(dstpath, basename + '_' + str(num) + '.' + ext), ext)
                        filepath = dstpath+'/'+ basename + '_' + str(num) + '.' + ext
                        BinaryImage(filepath)
                        num = num + 1
        else:
            print('Illegal ranks of splitting parameters！')


srclist = 'D:/teambition/sate_result/result'
filelist = []
if os.path.exists(srclist):
    dstpath = 'D:/teambition/sate_result/split'
    if (dstpath == '') or os.path.exists(dstpath):
        for filename in os.listdir(srclist):
            filename = srclist+"/"+filename
            filelist.append(filename)
        row = 1
        col = 3
        if row > 0 and col > 0:
            splitimage(filelist, row, col, dstpath)
        else:
            print('Invalid column splitting parameter！')
    else:
        print('Image output directory %s does not exist！' % dstpath)
else:
    print('Image input directory %s does not exist！！' % srclist)