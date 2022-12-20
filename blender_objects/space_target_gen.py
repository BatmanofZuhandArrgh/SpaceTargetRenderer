import cv2
import os
import yaml
import random
import glob
import numpy as np
import bpy
from pprint import pprint
from tempfile import TemporaryDirectory

from ast import literal_eval

from utils.bpy_utils import add_image_texture, append_bpy_object, create_image_texture, \
    set_bpy_obj_origin
from utils.img_utils import stitching_upwrapped_texture, IMG_EXT, get_random_color, get_solid_color_img
from utils.utils import get_yaml

class SpaceTargetGenerator():
    def __init__(self, config_dict) -> None:
        self.cubesat_dict = config_dict['cubesats']
        self.other_st_dict= config_dict['other_st']
        self.other_dict = config_dict['other']
        self.range_num_obj = literal_eval(config_dict['range_num_obj'])
    
        #Creating dictionaries of other space targets and their textures
        self.space_targets = {}    
        for dictionary in [self.other_dict, self.other_st_dict]:
            if dictionary['included']:
                blend_paths = [path for path in glob.glob(f'{dictionary["dir"]}/**', recursive = True) if path.split('.')[-1] == 'blend' ]
                blend_names = [os.path.splitext(os.path.basename(path))[0] for path in blend_paths]
                for i, blend_name in enumerate(blend_names):
                    self.space_targets[blend_name] = {}
                    self.space_targets[blend_name]['dir'] = blend_paths[i]
                    self.space_targets[blend_name]['textures'] = [path for path in glob.glob(f'{dictionary["textures"]}/**', recursive=True) if '.' + path.split('.')[-1].lower() in IMG_EXT]                    
                    self.space_targets[blend_name]['object_name'] = 'Other_ST'

        if self.cubesat_dict['included']:
            for key in self.cubesat_dict:
                if "U" in key:
                    self.space_targets[key] = {}
                    self.space_targets[key]['dir'] = self.cubesat_dict[key]
                    self.space_targets[key]['textures'] = [path for path in glob.glob(f'{self.cubesat_dict["textures"]}/**', recursive=True) if '.' + path.split('.')[-1].lower() in IMG_EXT]    
                    self.space_targets[key]['object_name'] = "Cube"

        # pprint(self.space_targets)

    def stitch_cube_texture(self, single_side_texture_path, obj_type):
        '''
        Input a path to an image texture of one side of the cubesat
        Output a path to an image texture of a cubesat of obj_type, output name {image_name}_{obj_type}.png
        '''
        obj_type = obj_type.lower()
        img_name = os.path.splitext(os.path.basename(single_side_texture_path))[0]
        out_img_name = img_name + '_' + obj_type

        texture_dir = single_side_texture_path.split('/one_side')[0]
        
        out_img_path = os.path.join(texture_dir, out_img_name+'.jpg')
    
        #50% chance of generating textures from existing images scraped from the web
        # if not os.path.exists(out_img_path) or 'random_color' in os.path.basename(out_img_path): #TODO consider removing already saved options for borders
            #If path does not already exist, use that path instead of stitching new texture
        stitching_upwrapped_texture(single_side_texture_path, obj_type, out_img_path)

        return out_img_path  

    def get_random_texture(self, texture_dir):
        '''
        Generate noise or constant color for texture
        '''
        if (random.randint(0,9) == 0): #10% chance of getting random noise
            out_img_path = os.path.join(texture_dir, 'random_noise.jpg')   
            img = np.random.normal(0,255,(640,640,3))
        else: #90% of getting random solid color
            out_img_path = os.path.join(texture_dir, 'random_color.jpg')
            img = get_solid_color_img(color=get_random_color(too_dark_sum_threshold=20))
        
        cv2.imwrite(img = img, filename=out_img_path)
        return out_img_path

    def get_texture_path(self, cur_obj_dict, obj_type):
        '''
        Return path to texture
        '''
        if cur_obj_dict['object_name'] == "Cube":
            if bool(random.getrandbits(1)): #50% chance of getting scraped img
                single_side_texture_path = random.choice(cur_obj_dict['textures']) 
            else: #50% chance of getting single side img of solid color or white noise
                single_side_texture_path = self.get_random_texture(os.path.dirname(cur_obj_dict['textures'][0]))

            image_texture_path = self.stitch_cube_texture(single_side_texture_path, obj_type)
            obj_type = 'CubeSat_' + obj_type

        elif cur_obj_dict['object_name'] == "Other_ST":
            if bool(random.getrandbits(1)): #50% chance of getting scraped img
                image_texture_path = random.choice(cur_obj_dict['textures'])
            else: #50% chance of getting random noise or solid color
                image_texture_path = self.get_random_texture(os.path.dirname(cur_obj_dict['textures'][0]))
            obj_type = 'OtherST_' + obj_type

        # print('Texture_PATH', image_texture_path)
            
        return obj_type, image_texture_path

    def generate(self):
        #By default, pipeline imports the space targets, instead of c
        num_obj = random.randrange(self.range_num_obj[0], self.range_num_obj[1])

        for i in range(num_obj):
            obj_type = random.choice([key for key in self.space_targets.keys()])
            cur_obj_dict = self.space_targets[obj_type]            
        
            obj_type, image_texture_path = self.get_texture_path(cur_obj_dict, obj_type)
        
            mat = create_image_texture(image_texture_path, mat_name=f"Material_{i}")

            object_name = append_bpy_object(
                blend_filepath=cur_obj_dict['dir'], 
                section='Object',
                object=cur_obj_dict['object_name']
                )

            obj = bpy.data.objects.get(object_name)
            obj.name = 'ST_' + obj_type + '_' + object_name + f'_{i}'
            set_bpy_obj_origin(obj.name, centering_mode = "ORIGIN_GEOMETRY", center="BOUNDS") #Since some of the obj doesn't have the origin as the geometry center already

            add_image_texture(obj, mat=mat)

def main():
    config_dict = get_yaml('pipeline_config.yaml')
    st_dict = config_dict['space_targets']
    space_target_generator = SpaceTargetGenerator(st_dict)
    space_target_generator.generate()
    pass

if __name__ == "__main__":
    main()

