import os
import io
import sys
import glob
#import argparse
import sqlite3 as lite
from PIL import Image
from datetime import datetime

def get_file_list(dir_path,extension_list):
    '''
    find all files in dir_path filter with extension list
    '''
    print dir_path
    os.chdir(dir_path)
    file_list = []
    for extension in extension_list:
        extension = '*.' + extension
        file_list += [os.path.realpath(e) for e in glob.glob(extension) ] 
    return file_list

def create_dir(base_dir):
    '''
    create dir (if not exists)
    '''
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)


def resize(w, h, w_box, h_box, pil_image):
    f1 = 1.0 * w_box / w
    f2 = 1.0 * h_box / h
    factor = min([f1, f2])
    width = int(w * factor)
    height = int(h * factor)
    return pil_image.resize((width, height), Image.ANTIALIAS)

def save_bin_file(file, bytes):
    '''
    save binary file
    '''
    file_stream = io.open(file,'wb')
    with file_stream:
        file_stream.write(bytes)

def get_bin_file(file):
    '''
    read binary file
    '''
    file_stream = io.open(file,'rb')
    with file_stream:
        return file_stream.read()

def save_image(image_file, image_bytes):
    data_stream = io.BytesIO(bytearray(image_bytes))
    pil_image = Image.open(data_stream)
    pil_image.save(image_file)


def get_rows(db_file):
    '''
    get all rows in metadata table of sqlite database
    '''
    cx = lite.connect(db_file)
    with cx:
        cx.row_factory = lite.Row # its key
        cu = cx.cursor() 
        cu.execute("select * from tiles") 
        for row in cu:
            yield row
        cu.close()

def process(input_file, output_dir):
    '''
    process sqlite tile file
    '''

    # process all rows in metadata table
    for row in get_rows(input_file):
        # column values
        zoom_level = row['zoom_level']
        tile_column = row['tile_column']
        tile_row = row['tile_row']
        tile_format = row['tile_format']
        data = row['tile_data']

        try:
            base_dir =  output_dir + '/15/' + str(tile_column)
            file_name = str(tile_row) + '_src'
            if tile_format == 2:
                file_name = file_name + ".jpg"
            if tile_format == 13:
                file_name = file_name + ".png"
            create_dir(base_dir)
            image_file = base_dir + '/' + file_name
            print image_file
            label_file = output_dir + '/15/' + str(tile_column) + '/'  + str(tile_row) + ".png"
            #if os.path.isfile(label_file):
            #    save_image(image_file, data)
            #save_image(image_file, data)
            if os.path.isdir(base_dir):
                save_image(image_file, data)
        except Exception, expinfo:
            print Exception,":",expinfo

def process_dir_list(input_dir_list):
    '''
    process input folder list, get sqlite db files in each folder and process data
    '''
    extension_list = ['tile']
    for input_dir in input_dir_list:
        db_file_list = get_file_list(input_dir, extension_list)
        for db_file in db_file_list:
            process(db_file, input_dir)

def process_file_list(db_list, out, db_url):
    '''
    process db file array
    '''
    for db_file in db_list:
        process(db_file, out, db_url)

if __name__ == '__main__':
    #parser = argparse.ArgumentParser()
    #parser.add_argument('-i', '--input', nargs='+')
    #parser.add_argument('-v', dest='verbose', action='store_true')
    #args = parser.parse_args()

    # save confige to variable
    #input_files = args.input
    #verbose = args.verbose

    input_files = ['D:\rs_sample_data\省界\河北']

    print '==========input args infos=========='

    print '==input-dirs:=='
    for dir in input_files:  
         print dir 
    
    print '==========start process==========='
    process_dir_list(input_files)
    
    print "process finished."
