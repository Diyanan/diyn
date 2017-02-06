# coding: utf-8  
# image_merge.py  
  
import os  
import Image  
  
def image_resize(img, size=(1500, 1100)):  
    try:  
        if img.mode not in ('L', 'RGB'):  
            img = img.convert('RGB')  
        img = img.resize(size)  
    except Exception, e:  
        pass  
    return img

def getChild(row, column, index):
    return row * 2 + index / 2, column * 2 + index % 2

def getParent(row, column):
    return row / 2, column / 2

def getChildIndex(row, column):
    return (row / 2) * 2 + column % 2

def getTile(row, column):
    return null
  
def image_merge(images, output_dir='output', output_name='merge.jpg',   
                restriction_max_width=None, restriction_max_height=None):  
    max_width = 0  
    total_height = 0  
    for img_path in images:  
        if os.path.exists(img_path):  
            img = Image.open(img_path)  
            width, height = img.size  
            if width > max_width:  
                max_width = width  
            total_height += height  
  
    new_img = Image.new('RGB', (max_width, total_height), 255)  
    x = y = 0  
    for img_path in images:  
        if os.path.exists(img_path):  
            img = Image.open(img_path)  
            width, height = img.size  
            new_img.paste(img, (x, y))  
            y += height  
  
    if restriction_max_width and max_width >= restriction_max_width:  
        ratio = restriction_max_height / float(max_width)  
        max_width = restriction_max_width  
        total_height = int(total_height * ratio)  
        new_img = image_resize(new_img, size=(max_width, total_height))  
  
    if restriction_max_height and total_height >= restriction_max_height:  
        ratio = restriction_max_height / float(total_height)  
        max_width = int(max_width * ratio)  
        total_height = restriction_max_height  
        new_img = image_resize(new_img, size=(max_width, total_height))  
      
    if not os.path.exists(output_dir):  
        os.makedirs(output_dir)  
    save_path = '%s/%s' % (output_dir, output_name)  
    new_img.save(save_path)  
    return save_path  

def getTilePath(base, row, column):
    res_dir = base + '/' + str(column)
    res_path = res_dir + '/' + str(row) + '_src.jpg'
    if not os.path.isfile(res_path):
        res_path = res_dir + '/' + str(row) + '_src.png'
    return res_path

def getLabelPath(base, row, column):
    return base + '/' + str(column) + '/' + str(row) + '.png'

def getResLabelPath(base, row, column):
    return base + '/' + str(column) + str(row) + '_src.png'

def mergeChildren(row, column,dim, input_dir, output_dir):
    new_img = Image.new('RGB', (dim, dim), 255)  
    have_children = False
    for i in range(0,4):
        crow , ccol = getChild(row, column, i)
        file = getTilePath(input_dir, crow, ccol)
        if os.path.exists(file):  
            img = Image.open(file)  
            width, height = img.size 
            y = (i / 2) * dim / 2
            x = (i % 2) * dim / 2
            new_img.paste(img, (x, y))  
            have_children = True 
    if not have_children:
        return
    #save_path = getTilePath(output_dir, row, column)
    res_dir = output_dir + '/' + str(column)
    save_path = res_dir + '/' + str(row) + '_src.jpg'
    dir = os.path.dirname(save_path)
    if not os.path.exists(dir):  
        os.makedirs(dir)  
    new_img.save(save_path)  

def mergeLabelChildren(row, column,dim, input_dir, output_dir):
    new_img = Image.new('RGBA', (dim, dim), 255)  
    have_children = False
    for i in range(0,4):
        crow , ccol = getChild(row, column, i)
        file = getLabelPath(input_dir, crow, ccol)
        if os.path.exists(file):  
            img = Image.open(file)  
            width, height = img.size 
            y = (i / 2) * dim / 2
            x = (i % 2) * dim / 2
            new_img.paste(img, (x, y))  
            have_children = True 
    if not have_children:
        return
    save_path = getLabelPath(output_dir, row, column)
    dir = os.path.dirname(save_path)
    if not os.path.exists(dir):  
        os.makedirs(dir)  
    new_img.save(save_path)  

def mergeResLabelChildren(row, column,dim, input_dir, output_dir):
    new_img = Image.new('L', (dim, dim), 255)  
    have_children = False
    for i in range(0,4):
        crow , ccol = getChild(row, column, i)
        file = getResLabelPath(input_dir, crow, ccol)
        if os.path.exists(file):  
            img = Image.open(file)  
            width, height = img.size 
            y = (i / 2) * dim / 2
            x = (i % 2) * dim / 2
            new_img.paste(img, (x, y)) 
            have_children = True 
    if not have_children:
        return
    save_path = getResLabelPath(output_dir, row, column)
    dir = os.path.dirname(save_path)
    if not os.path.exists(dir):  
        os.makedirs(dir)  
    new_img = image_resize(new_img, size=(256, 256))  
    new_img.save(save_path)  

def merge(input_dir, output_dir,dimention, startRow, startColumn, endRow, endColumn):
    for i in range(startRow+1, endRow+1):
        for j in range(startColumn+1, endColumn+1):
            mergeChildren(i,j,dimention,input_dir,output_dir)
            #mergeLabelChildren(i,j,dimention,input_dir,output_dir)
            #mergeResLabelChildren(i,j,dimention,input_dir,output_dir)

if __name__ == '__main__':  
    baseLevel = 15
    baseDir = 'D:/test2_tile'
    startRow, startColumn = (9226,53737)
    endRow, endColumn = (9296, 53855)
    baseDimention = 256
    for i in range(1, 6):
        input_dir = baseDir + '/' + str(baseLevel-i+1)
        output_dir = baseDir + '/' + str(baseLevel-i)
        startRow, startColumn = getParent(startRow, startColumn)
        endRow, endColumn = getParent(endRow, endColumn)
        baseDimention = baseDimention * 2
        merge(input_dir, output_dir,baseDimention, startRow, startColumn, endRow, endColumn)