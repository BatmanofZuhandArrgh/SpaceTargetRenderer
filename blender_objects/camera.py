from turtle import distance
import bpy
import numpy as np
import random

from ast import literal_eval

from utils.math_utils import get_random_point_on_3dpolygon, get_random_point_on_3dline, get_random_point_on_circle_xyplane
from utils.bpy_utils import get_calibration_matrix_K_from_blender, get_4x4_RT_matrix_from_blender, show_bpy_objects, get_rotation_euler_bpy_object
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

        self.camera_name = config_dict['camera_name']
        self.x, self.y, self.z = None, None, None
        self.rx, self.ry, self.rz = None, None, None
        
        self.extrinsic_matrix = None
        self.inv_intrinsic_matrix = None

        self.intrinsic_matrix = None
        self.inv_extrinsic_matrix = None

        self.st_range = config_dict['space_target_range']
        for key in self.st_range.keys():
            self.st_range[key] = literal_eval(self.st_range[key])

        self.cam_range = config_dict['cam2earth_range']
        for key in self.cam_range.keys():
                self.cam_range[key] = literal_eval(self.cam_range[key])
        
        #Earth measurements, if mode in ['empty_space_partial_earth', 'full_earth']
        self.earth_center = None
        self.earth_radius = None

    def update_earth_data(self, center, radius):
        self.earth_center = center
        self.earth_radius = radius

    def delete_existing_cameras(self):
        # Delete all existing cameras
        existing_cameras = [ob for ob in list(bpy.context.scene.objects) if ob.type == 'CAMERA']
        for camera in existing_cameras:
            camera_name = camera.name
            delete_bpy_object(camera_name)
    
    def randomize_camera_position(self):
        '''
        Determine the location of camera orbiting around earth
        Output: return the location and rotation of camera that can capture a perfect frame
        '''
        #1. Determine the distance of camera from (0,0,0), base on the tested range
        distance = random.uniform(self.cam_range['distance'][0], self.cam_range['distance'][1])

        #2. We wil only orbit the camera around the equator of earth, where it can capture a frame with light
        #So the camera will only be on 1 plane, where self.z = 0
        z = 0
        x, y = get_random_point_on_circle_xyplane(tuple(self.earth_center), radius=distance)
        #TODO update this with a function limiting the position, not too far back behind earth

        x, y, z = 0, -900, -0
        rx, ry, rz = radians(90), radians(90), radians(0)
        set_location_bpy_object(self.camera_name, x, y, z) #TODO DELETE THIS
        set_rotation_euler_bpy_object(self.camera_name, rx, ry, rz) #TODO DELETE THIS
        
        #3. Rotate the camera so within a limit of its existence 


    def create_camera(self, mode, creation_mode = 'create'):
        '''
        Create or import a camera. There should be only 1 camera
        '''

        if creation_mode == "import":            
            if mode == 'full_earth':
                #randomize camera distance from earth surface
                distance = random.uniform(-self.cam_range['distance'][0], -self.cam_range['distance'][1])
                set_location_bpy_object(self.camera_name, 0, distance, 0)
                set_rotation_euler_bpy_object(self.camera_name, radians(90), radians(90), radians(0))

            elif mode == 'empty_space_partial_earth':
                self.randomize_camera_position()

            else:
                raise ValueError(f'Not a valid mode {mode}')

            #Assuming the WIP blenderscene has already got a well setup camera, named "Camera" #TODO low priority, rename the object as Camera if name not Camera
            self.x, self.y, self.z, self.rx, self.ry, self.rz = \
                get_bpy_camera_coordinates()

        elif creation_mode == 'create':
            self.delete_existing_cameras()
            #Only ever create 1 camera. Current camera must be deleted before making another one
            camera_data = bpy.data.cameras.new(name=self.camera_name)
            camera_object = bpy.data.objects.new(self.camera_name, camera_data)
            bpy.context.scene.collection.objects.link(camera_object)
            bpy.context.scene.camera = camera_object

            if mode == 'empty_space':
                self.x, self.y, self.z = 7.3589, -6.9258, 4.9583
                self.rx, self.ry, self.rz = radians(63.6), 0, radians(46.7)

            elif mode == 'empty_space_partial_earth':
                #TODO edit general camera positioning
                #For earth_v1
                # self.x, self.y, self.z = 3.0638, -8.9029, -2.1132
                # self.rx, self.ry, self.rz = radians(89.6), radians(0), radians(89.6)
                
                #For earth_v2
                self.x, self.y, self.z = 0, -900, -0
                self.rx, self.ry, self.rz = radians(90), radians(90), radians(0)
                
            elif mode == "full_earth":
                self.x, self.y, self.z = 0, random.uniform(-900, -1800), 0
                self.rx, self.ry, self.rz = radians(90), radians(90), radians(0)

            else:
                raise ValueError(f'Not a valid mode {mode}')
            
            set_location_bpy_object(self.camera_name, self.x, self.y, self.z)
            set_rotation_euler_bpy_object(self.camera_name, self.rx, self.ry, self.rz)

        else:
            raise ValueError(f'Not a valid creation mode {creation_mode}')

        self.set_extrinsic_matrix()
        self.set_intrinsic_matrix()

    def random_roll_cam(self):
        #Rolling camera along its x-axis (outward axis)
        print('Rolling cam')
        #Getting extrinsic matrix from blender, not from calculated function get_4x4_RT_matrix_from_blender
        cam_obj = bpy.data.objects[self.camera_name]
        cam2world_mat = np.linalg.inv(np.array(cam_obj.matrix_world))[:3,:3]
        
        #Angle we want for the camera to roll along its x axis (It does not yaw or pitch), angle velocity (m/s) 
        omega = np.array([radians(np.random.uniform(low=0, high = 180, size=(1,))),0,0])
        rotation_diff = cam2world_mat.dot(omega)

        rotate_bpy_object(self.camera_name, rotation_diff[0], rotation_diff[1], rotation_diff[2])
        self.rx, self.ry, self.rz = get_rotation_euler_bpy_object(self.camera_name)

        self.set_extrinsic_matrix()
        self.set_intrinsic_matrix()

    def get_cam_location(self):
        #Return location set by camera generator
        return self.x, self.y, self.z
    
    def get_cam_rotation(self):
        #Return rotation set by camera generator
        return self.rx, self.ry, self.rz

    def set_extrinsic_matrix(self):
        #Needs to reset everytime the camera is moved or rotated
        self.extrinsic_matrix = get_4x4_RT_matrix_from_blender(bpy.data.objects[self.camera_name])
        self.inv_extrinsic_matrix = np.linalg.inv(self.extrinsic_matrix)

    def set_intrinsic_matrix(self):
        #Needs to reset everytime the camera is moved or rotated
        self.intrinsic_matrix = get_calibration_matrix_K_from_blender()
        # self.inv_intrinsic_matrix = np.linalg.inv(self.intrinsic_matrix) #Not used

    def get_extrinsic_matrix(self):
        return self.extrinsic_matrix
    
    def get_intrinsic_matrix(self):
        return self.intrinsic_matrix

    def get_focal_length(self):
        return bpy.data.cameras[0].lens

    def move_camera(self, x_offset, y_offset, z_offset):
        # By default there should only be 1 camera named "Camera"
        move_bpy_object(self.camera_name, x_offset, y_offset, z_offset)
    
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
    print(cam_gen.get_intrinsic_matrix())
    # sample_coord = np.array([1,2,3])
    # print(inv_ex_mat.dot(np.array([1,2,3,1])))
    # print(inv_ex_mat_3x4.dot(np.array([1,2,3])))

if __name__ == '__main__':
    main()