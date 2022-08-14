import os
import bpy
import subprocess
import tempfile
from math import radians
from utils import append_object

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
    blender_executable_path = '/home/anhnguyen/Downloads/blender-3.2.1-linux-x64/blender'
    output_rendered_file = 'test_basic_func.png'

    with tempfile.NamedTemporaryFile() as tmp_file:
        #Create temp filepath to save blend file
        blend_file_path = tmp_file.name        
        
        create_blend("", blend_file_path)
        render_file(
            executable=blender_executable_path,
            blend_file = blend_file_path,
            output_rendered_file = output_rendered_file,
        )

if __name__ == '__main__':
    main()