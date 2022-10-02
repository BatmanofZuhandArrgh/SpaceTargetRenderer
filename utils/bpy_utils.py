import os
import numpy as np
import bpy

from math_utils import get_random_rotation_offset

def append_bpy_object(blend_filepath, section, object = "Cube"):

    filepath  = os.path.join(blend_filepath, section, object)
    directory = os.path.join(blend_filepath, section)
    filename  = object

    bpy.ops.wm.append(
        filepath = filepath,
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

def get_bpy_objnames_by_substring(substring):
    return [name for name in get_bpy_objnames() if substring.lower() in name.lower()]

def get_bpy_obj_coord(obj_name):
    return bpy.data.objects[obj_name].location

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

def random_rotate_bpy_object(object_name):
    set_rotation_euler_bpy_object(object_name, get_random_rotation_offset(), get_random_rotation_offset(), get_random_rotation_offset())

def set_location_bpy_object(object_name, x, y, z):
    obj = bpy.data.objects[object_name]
    obj.location = (x, y, z)

def set_rotation_euler_bpy_object(object_name, x, y, z):
    obj = bpy.data.objects[object_name]
    obj.rotation_euler = (x, y, z)

def set_dimensions_bpy_object(object_name, x, y, z):
    obj = bpy.data.objects[object_name]
    obj.dimensions = (x, y, z)

def get_location_bpy_object(object_name):
    obj = bpy.data.objects[object_name]
    return obj.location

def get_rotation_euler_bpy_object(object_name):
    obj = bpy.data.objects[object_name]
    return obj.rotation_euler

def get_dimensions_bpy_object(object_name):
    obj = bpy.data.objects[object_name]
    return obj.dimensions

def change_background_color(hsva = (0, 0, 0, 1)):
    #Default is pitch black
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = hsva

def create_image_texture(image_texture_path, mat_name):
    mat = bpy.data.materials.new(name = mat_name)
    mat.use_nodes = True

    bsdf = mat.node_tree.nodes["Principled BSDF"]
    
    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.image = bpy.data.images.load(image_texture_path)

    mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])
    return mat

def add_image_texture(obj, mat):
    # Assign it to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

def count_bpy_object_bysubstring(substring = 'st_'):
    obj_names = get_bpy_objnames()
    return len([name for name in obj_names if substring.lower() in name.lower()]) 

def get_calibration_matrix_K_from_blender(mode='simple'):
    '''
    Get intrinsic matrix
    Source: https://mcarletti.github.io/articles/blenderintrinsicparams/
    '''
    scene = bpy.context.scene

    scale = scene.render.resolution_percentage / 100
    width = scene.render.resolution_x * scale # px
    height = scene.render.resolution_y * scale # px
    
    camdata = scene.camera.data

    if mode == 'simple':
        print(camdata.angle)
        aspect_ratio = width / height
        K = np.zeros((3,3), dtype=np.float32)
        K[0][0] = width / 2 / np.tan(camdata.angle / 2)
        K[1][1] = height / 2. / np.tan(camdata.angle / 2) * aspect_ratio
        K[0][2] = width / 2.
        K[1][2] = height / 2.
        K[2][2] = 1.
    
    if mode == 'complete':

        focal = camdata.lens # mm
        sensor_width = camdata.sensor_width # mm
        sensor_height = camdata.sensor_height # mm
        pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y

        if (camdata.sensor_fit == 'VERTICAL'):
            # the sensor height is fixed (sensor fit is horizontal), 
            # the sensor width is effectively changed with the pixel aspect ratio
            s_u = width / sensor_width / pixel_aspect_ratio 
            s_v = height / sensor_height
        else: # 'HORIZONTAL' and 'AUTO'
            # the sensor width is fixed (sensor fit is horizontal), 
            # the sensor height is effectively changed with the pixel aspect ratio
            pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
            s_u = width / sensor_width
            s_v = height * pixel_aspect_ratio / sensor_height

        # parameters of intrinsic calibration matrix K
        alpha_u = focal * s_u - 500
        alpha_v = focal * s_v - 500
        u_0 = width / 2
        v_0 = height / 2
        skew = 0 # only use rectangular pixels

        K = np.array([
            [alpha_u,    skew, u_0],
            [      0, alpha_v, v_0],
            [      0,       0,   1]
        ], dtype=np.float32)
    
    return K

# Returns camera rotation and translation matrices from Blender.
# 
# There are 3 coordinate systems involved:
#    1. The World coordinates: "world"
#       - right-handed
#    2. The Blender camera coordinates: "bcam"
#       - x is horizontal
#       - y is up
#       - right-handed: negative z look-at direction
#    3. The desired computer vision camera coordinates: "cv"
#       - x is horizontal
#       - y is down (to align to the actual pixel coordinates 
#         used in digital images)
#       - right-handed: negative z look-at direction

def get_4x4_RT_matrix_from_blender(cam):
    # bcam stands for blender camera
    R_bcam2cv = np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])

    # Transpose since the rotation is object rotation, 
    # and we want coordinate rotation
    # location, rotation = cam.matrix_world.decompose()[0:2]

    R_world2bcam = cam.rotation_euler.to_matrix().transposed()
    # Use matrix_world instead to account for all constraints    
    # R_world2bcam = rotation.to_matrix().transposed()

    # Convert camera location to translation vector used in coordinate changes
    T_world2bcam = -1*R_world2bcam @ cam.location
    # Use location from matrix_world to account for constraints:
    
    # Build the coordinate transform matrix from world to computer vision camera
    R_world2cv = R_bcam2cv@R_world2bcam
    T_world2cv = R_bcam2cv@T_world2bcam
    
    R_world2cv = np.concatenate((R_world2cv, np.zeros(shape=(1, 3))), axis = 0) #(3*4)
    T_world2cv = np.concatenate((T_world2cv.reshape(3,1), np.array([[1]])), axis = 0) #(3*1)

    RT = np.concatenate((R_world2cv, T_world2cv), axis = 1)

    return RT
