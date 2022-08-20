import os
import bpy
import subprocess
import tempfile
import yaml

from math import radians
from utils import * 
from bpy_utils import append_object
from space_target import SpaceTargetGenerator
from background import BackgroundGenerator

class RenderPipeline:
    def __init__(self, config_path = 'pipeline_config.yaml'):
        with open(config_path, "r") as stream:
            try:
                config_dict = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        self.blender_exe = config_dict['blender_exe']
        self.output_dir  = config_dict['output_dir']
        
        self.light_config = config_dict['light']
        self.camera_config = config_dict['camera']
        self.background_dict = config_dict['background']
        self.space_target_dict = config_dict['space_targets']
        print(self.background_dict)

        self.background_generator = BackgroundGenerator(self.background_dict)
        self.space_target_generator = SpaceTargetGenerator(self.space_target_dict) 

    def generate_background(self):
        self.background_generator.generate()

    def light_setup_n_positioning(self):
        pass

    def camera_setup(self):
        pass

    def camera_positioning(self):
        pass

    def generate_whole_scene(self):

        #Delete all default spawn objects in main scene
        bpy.ops.object.delete(use_global=False, confirm=False)
        
        pass


    def render_file(executable, blend_file, output_rendered_file, render_engine = 'BLENDER_EEVEE'):
        #https://docs.blender.org/manual/en/latest/advanced/command_line/render.html
        parameters = [executable, '-b', blend_file, '-o', output_rendered_file,'--engine', render_engine,'-f', '1']
        subprocess.call(parameters)
    
    def render(self):
        pass

    def run(self):
        for times in range(10):
            self.generate()


def test_cube_creation():
    bpy.ops.object.delete(use_global=False, confirm=False)

    #Create a cube
    bpy.ops.mesh.primitive_cube_add(enter_editmode=False, location=(0,0,0))

    # Delete object
    #bpy.ops.object.delete(use_global=False, confirm=False)

    #Assign active object
    so = bpy.context.active_object

    #Set location X
    so.location[0] = 0

    #Rotate set object
    so.rotation_euler[0] += radians(173)
    
    return so

def create_blend(blend_file_path, save_blend_file):
    append_blender_file = '/home/anhnguyen/Documents/Blender_Projects/Blender_fun/2U_test.blend'
    section = 'Object'

    #Create blend or modify blend, then save it to blend_file_path
    if blend_file_path not in [None, ""]:
        bpy.ops.wm.open_mainfile(filepath=blend_file_path)
    #else create a whole new blend file
    test_cube_creation()
    append_object(blend_filepath=append_blender_file, section=section)
    bpy.ops.wm.save_mainfile(filepath=save_blend_file)

def render_file(executable, blend_file, output_rendered_file, render_engine = 'BLENDER_EEVEE'):
    #https://docs.blender.org/manual/en/latest/advanced/command_line/render.html
    parameters = [executable, '-b', blend_file, '-o', output_rendered_file,'--engine', render_engine,'-f', '1']
    subprocess.call(parameters)

def main():
    pipeline = RenderPipeline()


    blender_executable_path = '/home/anhnguyen/Downloads/blender-3.2.1-linux-x64/blender'
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


if __name__ == '__main__':
    main()