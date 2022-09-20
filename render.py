import random
from re import X
import bpy
import subprocess
import tempfile
import yaml

from math import radians

from utils.math_utils import * 
from utils.bpy_utils import append_bpy_object, delete_bpy_object, get_bpy_objnames, get_bpy_objnames_by_substring, random_rotate_bpy_object, show_bpy_objects,\
     delete_bpy_object, delete_bpy_objects_by_name_substring, \
        random_rotate_bpy_object, count_bpy_object_bysubstring,\
            set_location_bpy_object, get_bpy_obj_coord
from blender_objects.space_target import SpaceTargetGenerator
from blender_objects.background import BackgroundGenerator
from blender_objects.camera import CameraGenerator
from blender_objects.light import LightGenerator

class RenderPipeline:
    def __init__(self, config_path = 'pipeline_config.yaml'):
        with open(config_path, "r") as stream:
            try:
                config_dict = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        self.blender_exe = config_dict['blender_exe']
        self.blender_engine = config_dict['blender_engine']
        self.output_dir  = config_dict['output_dir']
        self.WIP_blend_file_path = config_dict['WIP_blend_file_path']
        
        self.modes = config_dict['modes']
        self.light_config = config_dict['light']
        self.camera_config = config_dict['camera']
        self.background_dict = config_dict['background']
        self.space_target_dict = config_dict['space_targets']

        self.background_generator = BackgroundGenerator(self.background_dict)
        self.space_target_generator = SpaceTargetGenerator(self.space_target_dict) 

        self.light_generator = LightGenerator(config_dict=self.light_config)
        self.camera_generator = CameraGenerator(config_dict= self.camera_config)

        self.operational_config = config_dict['operation_config']

        #Current number of space target objects
        self.cur_st_objs = None

    def generate_background(self, mode):
        # Create background from scratch, or return WIP_blend_import path and creation_mode(import)
        return self.background_generator.generate(mode)

    def generate_space_targets(self):
        #Space targets are mode-ignorant
        return self.space_target_generator.generate()

    def light_setup_n_positioning(self, mode, creation_mode):
        self.light_generator.create_light(mode, creation_mode)

    def camera_setup_n_positioning(self, mode, creation_mode):
        self.camera_generator.create_camera(mode, creation_mode)

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
        coordinates_within_cam_FOV = self.camera_generator.get_st_positions_within_FOV(len(self.cur_st_objs))
        for i in range(len(self.cur_st_objs)):
            set_location_bpy_object(
                object_name=self.cur_st_objs[i],
                x=coordinates_within_cam_FOV[i][0],
                y=-coordinates_within_cam_FOV[i][1], 
                z=coordinates_within_cam_FOV[i][2],
            )

    def space_target_rotating(self):
        #Randomly rotating space targets
        for obj_name in self.cur_st_objs:
            random_rotate_bpy_object(object_name=obj_name)
        
    def open_WIP_blend(self):
        # Opening WIP blend file path to append objects in 
        if self.WIP_blend_file_path not in [None, ""]:
            bpy.ops.wm.open_mainfile(filepath=self.WIP_blend_file_path)     

    def delete_all_space_targets(self):
        delete_bpy_objects_by_name_substring('st_')             
        delete_bpy_objects_by_name_substring('cube')
        pass  
    
    def work_on_existing_blend(self):
        self.open_WIP_blend()
        self.delete_all_space_targets()

    def render(self):
        #https://docs.blender.org/manual/en/latest/advanced/command_line/render.html
        #Create temp filepath to save blend file
        with tempfile.NamedTemporaryFile() as tmp_file:
            blend_file_path = tmp_file.name   
            
            for cycle in range(self.operational_config['num_cycle']):
                #For every cycle, create background, set up light and camera
                mode =  random.choice(self.modes)   
                mode = 'empty_space' #_partial_earth' #_partial_earth' #TODO Delete this

                self.WIP_blend_file_path, creation_mode = self.generate_background(mode)
                # WIP_blend_file_path might be supplied if background is imported
                self.work_on_existing_blend()

                self.light_setup_n_positioning(mode, creation_mode)

                self.camera_setup_n_positioning(mode, creation_mode)

                for iter in range(self.operational_config['num_iter_per_cycle']):
                    # For every iteration, space targets are generated
                    self.generate_space_targets()
                    self.cur_st_objs = get_bpy_objnames_by_substring('st_')

                    for view in range(self.operational_config['num_view_per_iter']):            
                        #For every view, space targets are repositioned and rotates.
                        #Camera rotates by 90
                        self.space_target_rotating()
                        self.space_target_positioning()  
                        # self.camera_rotating()                      
                        
                        #Render
                        img_path = f'{self.output_dir}/c{cycle}_i{iter}_v{view}.png'
                        bpy.ops.wm.save_mainfile(filepath=blend_file_path)
                        
                        # print('cam coord', self.camera_generator.get_camera_coordinates())
                        # show_bpy_objects()
                        parameters = [self.blender_exe, '-b', blend_file_path, '-o', img_path,'--engine', self.blender_engine,'-f', '1']
                        subprocess.call(parameters)

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