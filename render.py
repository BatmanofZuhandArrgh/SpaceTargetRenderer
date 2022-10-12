from ast import literal_eval
from functools import partial
import os
import random
import bpy
import subprocess
import tempfile
import yaml
import cv2

from math import radians
from blender_objects.cubesat import CubeSat
from pprint import pprint
from blender_objects.other_ST import Other_ST

from utils.utils import get_yaml
from utils.math_utils import * 
from utils.bpy_utils import append_bpy_object, delete_bpy_object, get_bpy_objnames, get_bpy_objnames_by_substring, \
    random_rotate_bpy_object, show_bpy_objects,\
     delete_bpy_object, delete_bpy_objects_by_name_substring, \
        random_rotate_bpy_object, count_bpy_object_bysubstring,\
            set_location_bpy_object, get_bpy_obj_coord, set_render_img_size,\
            render_region

from blender_objects.space_target import SpaceTargetGenerator
from blender_objects.background import BackgroundGenerator
from blender_objects.camera import CameraGenerator
from blender_objects.light import LightGenerator

class RenderPipeline:
    def __init__(self, config_path = 'pipeline_config.yaml'):
        config_dict = get_yaml(config_path)

        self.blender_exe = config_dict['blender_exe']
        self.blender_engine = config_dict['blender_engine']
        self.output_dir  = config_dict['output_dir']
        self.WIP_blend_file_path = config_dict['WIP_blend_file_path']
        
        self.modes = config_dict['modes']
        self.light_config = config_dict['light']
        self.camera_config = config_dict['camera']
        self.background_dict = config_dict['background']
        self.space_target_dict = config_dict['space_targets']
        self.label_dict = get_yaml(config_dict['label_dict'])

        self.img_size = literal_eval(config_dict['img_size'])

        self.background_generator = BackgroundGenerator(self.background_dict)
        self.space_target_generator = SpaceTargetGenerator(self.space_target_dict) 

        self.light_generator = LightGenerator(config_dict=self.light_config)
        self.camera_generator = CameraGenerator(config_dict= self.camera_config)

        self.operational_config = config_dict['operation_config']

        #Current number of space target objects
        self.cur_st_obj_names = None #Current name of all space targets 
        self.st_coords_world = None
        self.st_coords_cam = None
        self.st_coords_img = None
        self.cur_st_objs = {} #Current dict of current SpaceTargets

        self.intrinsic_mat = None
        self.extrinsic_mat = None

    def generate_background(self, mode):
        # Create background from scratch, or return WIP_blend_import path and creation_mode(import)
        return self.background_generator.generate(mode)

    def generate_space_targets(self):
        #Space targets are mode-ignorant        
        self.space_target_generator.generate()
        self.cur_st_obj_names = get_bpy_objnames_by_substring('st_')
        self.init_st_dict()

    def init_st_dict(self):
        self.cur_st_objs.clear() #Clear before populating with new objs
        for name in self.cur_st_obj_names:

            print(name)
            if 'CubeSat' in name:
                self.cur_st_objs[name] = CubeSat(
                    obj_name=name,
                    img_coord=(0,0),
                    cam_coord=(0,0,0),
                    world_coord=(0,0,0)
                )

            elif 'OtherST' in name:
                self.cur_st_objs[name] = Other_ST(
                    obj_name=name,
                    img_coord=(0,0),
                    cam_coord=(0,0,0),
                    world_coord=(0,0,0)
                )


    def light_setup_n_positioning(self, mode, creation_mode):
        self.light_generator.create_light(mode, creation_mode)

    def camera_setup_n_positioning(self, mode, creation_mode):
        self.camera_generator.create_camera(mode, creation_mode)
        self.intrinsic_mat = self.camera_generator.get_intrinsic_matrix()
        self.extrinsic_mat = self.camera_generator.get_extrinsic_matrix()

    def camera_positioning(self, position):
        pass

    def camera_rotating(self):
        self.camera_generator.rotate_by_90()
    
    def space_target_positioning(self):
        '''
        Randomly position space targets
        Get st coordinates from camera_generator
        and move the curre
        '''
        self.st_coords_cam, self.st_coords_world = self.camera_generator.get_st_positions_within_FOV(len(self.cur_st_obj_names))
        for i in range(len(self.cur_st_obj_names)):
            set_location_bpy_object(
                object_name=self.cur_st_obj_names[i],
                x=self.st_coords_world[i][0],
                y=self.st_coords_world[i][1], 
                z=self.st_coords_world[i][2],
            )

        # self.st_coords_cam = [-np.array(coord) for coord in self.st_coords_cam]
        self.st_coords_img = [self.intrinsic_mat.dot(coords[:-1]) for coords in self.st_coords_cam]
        self.st_coords_img = [((coord/coord[2]).astype(int))[:-1] for coord in self.st_coords_img]

    def space_target_rotating(self):
        #Randomly rotating space targets
        for obj_name in self.cur_st_obj_names:
            random_rotate_bpy_object(object_name=obj_name)

    def space_target_updating(self):
        #Update coords and rotation for every iteration
        for i in range(len(self.cur_st_obj_names)):
            self.cur_st_objs[self.cur_st_obj_names[i]].update(
                world_coord = self.st_coords_world[i], 
                cam_coord = self.st_coords_cam[i], 
                img_coord = self.st_coords_img[i]
            )

            self.cur_st_objs[self.cur_st_obj_names[i]].update_bbox(self.intrinsic_mat, self.extrinsic_mat)
        
    def delete_all_space_targets(self):
        delete_bpy_objects_by_name_substring('st_')             
        delete_bpy_objects_by_name_substring('cube')
        pass
    
    def init_blend(self):     
        # Opening WIP blend file path to append objects, if not start new one 
        if self.WIP_blend_file_path not in [None, ""]:
            bpy.ops.wm.open_mainfile(filepath=self.WIP_blend_file_path) 
            self.background_generator.replace_cloud()  
            self.background_generator.randomize_bloom()        
        else:
            bpy.ops.wm.read_homefile(use_empty=True)

        self.delete_all_space_targets()
        set_render_img_size(self.img_size)

    def modify_environment(self, mode):
        if mode == 'empty_space_partial_earth':
            self.background_generator.modify_earth()
        elif mode == 'empty_space':
            pass

    def render(self):
        #https://docs.blender.org/manual/en/latest/advanced/command_line/render.html            
        for cycle in range(self.operational_config['num_cycle']):
            #For every cycle, create background, set up light and camera
            mode =  random.choice(self.modes)   
            # mode = 'empty_space' #_partial_earth' #_partial_earth' #TODO Delete this

            #Create temp filepath to save blend file
            with tempfile.NamedTemporaryFile() as tmp_file:
                blend_file_path = tmp_file.name   

                self.WIP_blend_file_path, creation_mode = self.generate_background(mode)
                
                # WIP_blend_file_path might be supplied if background is imported
                self.init_blend()

                self.light_setup_n_positioning(mode, creation_mode)

                self.camera_setup_n_positioning(mode, creation_mode)

                for iter in range(self.operational_config['num_iter_per_cycle']):
                    # For every iteration, space targets are generated
                    self.generate_space_targets()

                    for view in range(self.operational_config['num_view_per_iter']):            
                        #For every view, space targets are repositioned and rotates.
                        #Camera rotates by 90
                        self.space_target_rotating()
                        self.space_target_positioning()  
                        self.space_target_updating()
                        self.modify_environment(mode)
                        
                        # render_region() #Does not work, increase cloud generation time
                        
                        #Render                         
                        img_path = os.path.join(self.output_dir,f'c{cycle}_i{iter}_v{view}')
                        bpy.ops.wm.save_mainfile(filepath=blend_file_path)
                        
                        parameters = [self.blender_exe, '-b', blend_file_path, '-o', img_path,'--engine', self.blender_engine,'-f', '1']
                        subprocess.call(parameters)
                        
                        #Draw bounding box
                        img_path = os.path.splitext(img_path)[0] + '0001.png'
                        cur_img = cv2.imread(img_path)
                        labels = []
                        for name in self.cur_st_obj_names:
                            center_coord = self.cur_st_objs[name].img_coord
                            bbox_width = self.cur_st_objs[name].bbox[1][0] - self.cur_st_objs[name].bbox[0][0]
                            bbox_height = self.cur_st_objs[name].bbox[1][1] - self.cur_st_objs[name].bbox[0][1]

                            cv2.circle(cur_img, (center_coord[0], center_coord[1]), radius=2, color=(0,0, 255), thickness=2)
                            cur_img = cv2.rectangle(cur_img, self.cur_st_objs[name].bbox[0], self.cur_st_objs[name].bbox[1], color =(255,0, 0), thickness = 2)
                            label = [
                                str(self.label_dict[self.cur_st_objs[name].cls_type]), 
                                str(round(center_coord[0]/self.img_size[0], 2)), 
                                str(round(center_coord[1]/self.img_size[1], 2)), 
                                str(round(bbox_width/self.img_size[0], 2)),
                                str(round(bbox_height/self.img_size[1], 2))
                            ]
                            labels.append(' '.join(label))

                        cv2.imwrite(filename=img_path, img=cur_img)
                        
                        #Output text
                        txt_name = os.path.splitext(os.path.basename(img_path))[0] + '.txt'
                        txt_path = os.path.join(self.output_dir, txt_name)

                        with open(txt_path, 'w') as f:
                            f.write('\n'.join(labels))

                        print('=======================================')

                self.WIP_blend_file_path = "" #Reset TODO Refactor
def main():
    pipeline = RenderPipeline()

    # blender_executable_path = '/home/anhnguyen/Downloads/blender-3.2.1-linux-x64/blender'
    # output_rendered_file = 'test_basic_func.png'

    # with tempfile.NamedTemporaryFile() as tmp_file:
    #     #Create temp filepath to save blend file
    #     blend_file_path = tmp_file.name        
        
    #     create_blend("", blend_file_path)
    #     render_file(
    #         executable=blender_executable_path,
    #         blend_file = blend_file_path,
    #         output_rendered_file = output_rendered_file,
    #     )

    pipeline.render()

if __name__ == '__main__':
    main()