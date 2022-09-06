import os
import bpy

def append_bpy_object(blend_filepath, section, object = "Cube"):

    filepath  = os.path.join(blend_filepath, section, object)
    directory = os.path.join(blend_filepath, section)
    filename  = object

    bpy.ops.wm.append(
        filename=filename,
        directory=directory)

def show_bpy_objects(print_them = True):
    objs = list(bpy.data.objects)
    if print_them:
        print("List of objects",objs)
        print("List of types", [x.type for x in objs])
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
    '''
    Delete bpy object from scene by the object's name
    '''
    # Gives out info warning, messy for the console
    # Not neccessary to using this function
    # bpy.data.objects[object_name].select_set(True)
    # bpy.ops.object.delete()

    object_to_delete = bpy.data.objects[object_name]
    bpy.data.objects.remove(object_to_delete, do_unlink=True)

def get_bpy_objnames():
    objs = show_bpy_objects(print_them=False)
    obj_names = [obj.name for obj in objs]
    return obj_names

def clear_all_bpy_objects():
    obj_names = get_bpy_objnames()
    for name in obj_names:
        delete_bpy_object(name)

def delete_bpy_objects_by_name_substring(name_substring):
    obj_names = get_bpy_objnames()
    obj_names_2b_deleted = [name for name in obj_names if name_substring.lower() in name.lower()]
    for name in obj_names_2b_deleted:
        delete_bpy_object(name)

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

def change_background_color(hsva = (0, 0, 0, 1)):
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = hsva

def add_light(type):
    bpy.ops.object.light_add(type=type, radius=1, location=(0, 0, 0))
    