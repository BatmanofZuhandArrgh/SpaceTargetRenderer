import bpy
import numpy as np

from ast import literal_eval

from utils.math_utils import get_random_point_on_3dpolygon, get_random_point_on_3dline
from utils.bpy_utils import get_calibration_matrix_K_from_blender, get_4x4_RT_matrix_from_blender, show_bpy_objects
from utils.utils import get_yaml

np.set_printoptions(suppress=True)

from math import radians, cos, sin
from utils.bpy_utils import delete_bpy_object, move_bpy_object,\
     select_bpy_object, select_bpy_object,\
         set_location_bpy_object, set_rotation_euler_bpy_object,\
            rotate_bpy_object, get_bpy_camera_coordinates

class CameraGenerator():
    def __init__(self, config_dict) -> None:
        #By default
        self.config_dict = config_dict

        self.x, self.y, self.z = None, None, None
        self.rx, self.ry, self.rz = None, None, None
        
        self.extrinsic_matrix = None
        self.intrinsic_matrix = None
        self.inv_extrinsic_matrix = None

        self.st_range = config_dict['space_target_range']
        for key in self.st_range.keys():
            self.st_range[key] = literal_eval(self.st_range[key])

    def delete_existing_cameras(self):
        # Delete all existing cameras
        existing_cameras = [ob for ob in list(bpy.context.scene.objects) if ob.type == 'CAMERA']
        for camera in existing_cameras:
            camera_name = camera.name
            delete_bpy_object(camera_name)

    def create_camera(self, mode, creation_mode = 'create'):
        '''
        Create or import a camera. There should be only 1 camera
        '''
        camera_name = "Camera"

        if creation_mode == "import":
            #Assuming the WIP blenderscene has already got a well setup camera, named "Camera"
            self.x, self.y, self.z, self.rx, self.ry, self.rz = \
                get_bpy_camera_coordinates()
            
            self.set_extrinsic_matrix()
            self.set_intrinsic_matrix()
            return

        self.delete_existing_cameras()
        #Only ever create 1 camera. Current camera must be deleted before making another one
        camera_data = bpy.data.cameras.new(name=camera_name)
        camera_object = bpy.data.objects.new(camera_name, camera_data)
        bpy.context.scene.collection.objects.link(camera_object)
        bpy.context.scene.camera = camera_object

        if mode == 'empty_space':
            self.x, self.y, self.z = 7.3589, -6.9258, 4.9583
            self.rx, self.ry, self.rz = radians(63.6), 0, radians(46.7)

        elif mode == 'empty_space_partial_earth':
            #TODO edit general camera positioning
            self.x, self.y, self.z = 3.0638, -8.9029, -2.1132
            self.rx, self.ry, self.rz = radians(89.6), radians(0), radians(89.6)

        elif mode == "full_earth":
            self.x, self.y, self.z = 0, 0, 0
            self.rx, self.ry, self.rz = 0, 0, 0

        set_location_bpy_object(camera_name, self.x, self.y, self.z)
        set_rotation_euler_bpy_object(camera_name, self.rx, self.ry, self.rz)

        self.set_extrinsic_matrix()
        self.set_intrinsic_matrix()

    def rotate_by_90(self):
        self.rz += radians(90)
        rotate_bpy_object("Camera", 0, 0, radians(90))
          
    def get_cam_location(self):
        #Return location set by camera generator
        return self.x, self.y, self.z
    
    def get_cam_rotation(self):
        #Return rotation set by camera generator
        return self.rx, self.ry, self.rz

    def set_extrinsic_matrix(self):
        self.extrinsic_matrix = get_4x4_RT_matrix_from_blender(bpy.data.objects['Camera'])
        self.inv_extrinsic_matrix = np.linalg.inv(self.extrinsic_matrix)

    def set_intrinsic_matrix(self):
        self.intrinsic_matrix = get_calibration_matrix_K_from_blender()

    def get_extrinsic_matrix(self):
        return self.extrinsic_matrix
    
    def get_intrinsic_matrix(self):
        return self.intrinsic_matrix

    def get_focal_length(self):
        return bpy.data.cameras[0].lens

    def move_camera(self, x_offset, y_offset, z_offset):
        # By default there should only be 1 camera named "Camera"
        move_bpy_object("Camera", x_offset, y_offset, z_offset)
    
    def get_camera_coordinates(self):
        return self.get_cam_location() + self.get_cam_rotation() 
    
    def get_st_positions_within_FOV(self, num_objs):
        furthest_surface_points = get_random_point_on_3dpolygon(
            num_points= num_objs,
            max_abs_x= self.st_range['horizontal_dist'][-1],
            max_abs_y= self.st_range['vertical_dist'][-1], 
            z_coord= self.st_range['depth'][-1]
            )

        closest_surface_points = get_random_point_on_3dpolygon(
            num_points= num_objs, 
            max_abs_x= self.st_range['horizontal_dist'][0],
            max_abs_y= self.st_range['vertical_dist'][0], 
            z_coord= self.st_range['depth'][0]
            )

        points_camCoord = []
        for point_pair in zip(furthest_surface_points, closest_surface_points):
            points_camCoord.append(
                get_random_point_on_3dline(point_pair[0], point_pair[1]).tolist()
            )
        
        points_camCoord = [point + [1] for point in points_camCoord]
        points_worldCoord = [self.inv_extrinsic_matrix.dot(np.array(coord)) for coord in points_camCoord]
        points_worldCoord = [coord[:-1] for coord in points_worldCoord]
        
        return points_camCoord, points_worldCoord

def main():
    import yaml
    config_dict = get_yaml('./pipeline_config.yaml')

    cam_gen = CameraGenerator(config_dict=config_dict['camera'])
    cam_gen.create_camera(mode='empty_space')
    ex_mat = cam_gen.get_extrinsic_matrix()
    inv_ex_mat = np.linalg.inv(ex_mat)
    # inv_ex_mat_3x4 = inv_ex_mat[:-1,:] #Remove the bottom [0,0,0,1] row

    # sample_coord = np.array([1,2,3])
    # print(inv_ex_mat.dot(np.array([1,2,3,1])))
    # print(inv_ex_mat_3x4.dot(np.array([1,2,3])))

if __name__ == '__main__':
    main()