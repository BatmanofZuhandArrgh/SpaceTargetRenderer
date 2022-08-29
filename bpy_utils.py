import os
import bpy

def append_bpy_object(blend_filepath, section, object = "Cube"):

    filepath  = os.path.join(blend_filepath, section, object)
    directory = os.path.join(blend_filepath, section)
    filename  = object

    bpy.ops.wm.append(
        filename=filename,
        directory=directory)

def show_bpy_objects():
    objs = list(bpy.data.objects)
    print("List of objects",objs)
    return objs

def show_bpy_objmode():
    mode = bpy.ops.object.mode
    print("Mode", mode)
    return mode

def set_bpy_objmode(mode):
    bpy.ops.object.mode_set(mode = mode)

def select_bpy_object(object_name):
    # bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[object_name].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[object_name]

def delete_bpy_object(object_name):
    # Gives out info warning, messy for the console
    # Not neccessary
    # if bpy.context.object.mode == 'EDIT':
    #     bpy.ops.object.mode_set(mode='OBJECT')
    # deselect all objects
    # bpy.ops.object.select_all(action='DESELECT')
    # # select the object
    # bpy.data.objects[object_name].select_set(True)
    # # delete all selected objects
    # bpy.ops.object.delete()

    object_to_delete = bpy.data.objects[object_name]
    bpy.data.objects.remove(object_to_delete, do_unlink=True)

def move_bpy_object(object_name, x_offset, y_offset, z_offset):
    obj = bpy.data.objects[object_name]
    obj.location.x += x_offset
    obj.location.y += y_offset
    obj.location.z += z_offset

def rotate_bpy_object(object_name, x_offset, y_offset, z_offset):
    obj = bpy.data.objects[object_name]
    obj.rotation_euler.x += x_offset
    obj.rotation_euler.y += y_offset
    obj.rotation_euler.z += z_offset

def set_location_bpy_object(object_name, x, y, z):
    obj = bpy.data.objects[object_name]
    obj.location = (x, y, z)

def set_rotation_euler_bpy_object(object_name, x, y, z):
    obj = bpy.data.objects[object_name]
    obj.rotation_euler = (x, y, z)