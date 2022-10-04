#Inspired by https://github.com/jerryWTMH/yolo2coco/blob/main/yolo2coco.py

import os
import json
import cv2

from ast import literal_eval
from utils.utils import get_yaml

id_counter = 0 # To record the id
out = {'annotations': [], 
           'categories': [{"id": 1, "name": "cricoid_cartilage", "supercategory": ""}, {"id": 2, "name": "thyroid_cartilage", "supercategory": ""}], ##### change the categories to match your dataset!
           'images': [],
           'info': {"contributor": "", "year": "", "version": "", "url": "", "description": "", "date_created": ""},
           'licenses': {"id": 0, "name": "", "url": ""}
           }

def annotations_data(whole_path , image_id, img_size):
    # id, bbox, iscrowd, image_id, category_id
    width, height = img_size
    global id_counter
    txt = open(whole_path,'r')
    for line in txt.readlines(): # if txt.readlines is null, this for loop would not run
        data = line.strip()
        data = data.split() 
        # convert the center into the top-left point!
        data[1] = float(data[1])* width - 0.5 * float(data[3])* width ##### change the 800 to your raw image width
        data[2] = float(data[2])* height - 0.5 * float(data[4])* width ##### change the 600 to your raw image height
        data[3] = float(data[3])* width ##### change the 800 to your raw image width
        data[4] = float(data[4])* height ##### change the 600 to your raw image height
        bbox = [data[1],data[2],data[3],data[4]]
        ann = {'id': id_counter,
            'bbox': bbox,
            'area': data[3] * data[4],
            'iscrowd': 0,
            'image_id': image_id,
            'category_id': int(data[0]) + 1            
        }
        out['annotations'].append(ann)
        id_counter = id_counter + 1 

def images_data(file_name, img_size):
    #id, height, width, file_name
    id = file_name.split('.')[0]
    file_name = id + '.png' ##### change '.jpg' to other image formats if the format of your image is not .jpg
    imgs = {'id': id,
            'height': img_size[1], ##### change the 600 to your raw image height
            'width': img_size[0], ##### change the 800 to your raw image width
            'file_name': file_name,
            "coco_url": "", 
            "flickr_url": "", 
            "date_captured": 0, 
            "license": 0
    }
    out['images'].append(imgs)                    

if __name__ == '__main__':
    config_dict = get_yaml('pipeline_config.yaml')
    img_size = literal_eval(config_dict['img_size'])
    folder_path = './sample/output' #####

    files = os.listdir(folder_path)
    files.sort()
    for file in files:
        whole_path = os.path.join(folder_path,file)
        if '.txt' in whole_path:
            annotations_data(whole_path, file.split('.')[0], img_size)
        elif '.png' in whole_path:
            images_data(file, img_size)

    output_path = './sample'
    with open(f'{output_path}/sample.json', 'w') as outfile: ##### change the str to the json file name you want
      json.dump(out, outfile, separators=(',', ':'))