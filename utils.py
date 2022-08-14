import os
import bpy

def append_object(blend_filepath, section, object = "Cube"):

    filepath  = os.path.join(blend_filepath, section, object)
    directory = os.path.join(blend_filepath, section)
    filename  = object
    print(directory, filename)

    bpy.ops.wm.append(
        filename=filename,
        directory=directory)
