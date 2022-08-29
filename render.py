import os
import bpy
import subprocess
import tempfile
import yaml

from math import radians

from utils import * 
from bpy_utils import append_bpy_object, delete_bpy_object, show_bpy_objects, delete_bpy_object
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
        self.input_blend = config_dict['input_blend']
        self.WIP_blend_file_path = config_dict['WIP_blend_file_path']
        
        self.light_config = config_dict['light']
        self.camera_config = config_dict['camera']
        self.background_dict = config_dict['background']
        self.space_target_dict = config_dict['space_targets']

        self.background_generator = BackgroundGenerator(self.background_dict)
        self.space_target_generator = SpaceTargetGenerator(self.space_target_dict) 

        self.light = LightGenerator(config_dict)
        self.camera_generator = CameraGenerator(config_dict= self.camera_config)

        self.operational_config = config_dict['operation_config']

    def generate_background(self):
        self.background_generator.generate()

    def generate_space_targets(self):
        self.space_target_generator.generate()

    def light_setup_n_positioning(self):
        pass

    def camera_setup(self):
        self.camera_generator.setup()

    def camera_positioning(self, position):
        pass
    
    def space_target_positioning(self):
        pass

    def space_target_rotation(self):
        pass

    def render(self):
        #https://docs.blender.org/manual/en/latest/advanced/command_line/render.html
        #Create temp filepath to save blend file
        with tempfile.NamedTemporaryFile() as tmp_file:
            blend_file_path = tmp_file.name   
            
            #Delete default cube
            delete_bpy_object("Cube")

            # Opening WIP blend file path to append objects in 
            if self.WIP_blend_file_path not in [None, ""]:
                bpy.ops.wm.open_mainfile(filepath=self.WIP_blend_file_path)

            for cycle in range(self.operational_config['num_cycle']):
                #For every cycle, create background, set up light and camera
                self.generate_background()
                self.light_setup_n_positioning()

                show_bpy_objects()
                self.camera_setup()
                show_bpy_objects()


                for iter in range(self.operational_config['num_iter_per_cycle']):
                    # For every iteration, space targets are generated
                    self.generate_space_targets()
                                    
                    for view in range(self.operational_config['num_view_per_iter']):            
                        #For every view, space targets are repositioned and rotated
                        position = self.space_target_positioning()

                        for i in range(1): #TODO EDIT number of turns to relocate the camera
                            #Relocating and rotating camera
                            self.camera_positioning(position)       
                            self.space_target_rotation()                        
                            
                            #Render
                            img_path = f'{self.output_dir}/c{cycle}_i{iter}_v{view}_{i}.png'
                            bpy.ops.wm.save_mainfile(filepath=blend_file_path)
                            # parameters = [self.blender_exe, '-b', blend_file_path, '-o', img_path,'--engine', self.blender_engine,'-f', '1']
                            # subprocess.call(parameters)


def create_blend(blend_file_path, save_blend_file):
    append_blender_file = '/home/anhnguyen/Documents/Blender_Projects/Blender_fun/2U_test.blend'
    section = 'Object'

    #Create blend or modify blend, then save it to blend_file_path
    if blend_file_path not in [None, ""]:
        bpy.ops.wm.open_mainfile(filepath=blend_file_path)

    #else create a whole new blend file
    # test_cube_creation()
    append_bpy_object(blend_filepath=append_blender_file, section=section)
    bpy.ops.wm.save_mainfile(filepath=save_blend_file)

def render_file(executable, blend_file, output_rendered_file, render_engine = 'BLENDER_EEVEE'):
    #https://docs.blender.org/manual/en/latest/advanced/command_line/render.html
    parameters = [executable, '-b', blend_file, '-o', output_rendered_file,'--engine', render_engine,'-f', '1']
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