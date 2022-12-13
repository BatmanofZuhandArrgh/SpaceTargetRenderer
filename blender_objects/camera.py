from turtle import distance
import bpy
import numpy as np
import random

from ast import literal_eval

from utils.math_utils import get_random_point_on_3dpolygon, get_random_point_on_3dline, get_random_point_on_sphere, \
    get_random_point_within_intersecting_tangent_circle_between_point_n_sphere, get_random_tangent_point_between_point_n_sphere
from utils.bpy_utils import get_calibration_matrix_K_from_blender, get_4x4_RT_matrix_from_blender, get_rotation_euler_bpy_object, \
    get_cam_angle_to_look_at, deselect_bpy_object, set_dof_distance
from utils.utils import get_yaml

np.set_printoptions(suppress=True)

from math import radians, cos, sin
from utils.bpy_utils import delete_bpy_object, move_bpy_object,\
     select_bpy_object, select_bpy_object,\
         set_location_bpy_object, set_rotation_euler_bpy_object,\
            rotate_bpy_object, get_bpy_camera_coordinates
from utils.math_utils import degrees

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
    
    def randomize_camera_location(self):
        '''
        Determine the location of camera orbiting around earth
        Output: return the location and rotation of camera that can capture a perfect frame
        '''
        #1. Determine the distance of camera from (0,0,0), base on the tested range
        distance = random.uniform(self.cam_range['distance'][0], self.cam_range['distance'][1])

        #2. We wil only orbit the camera on the bright side of the earth, where it can capture a frame with light
        is_on_brightside = False
        while not is_on_brightside:
            x, y, z = get_random_point_on_sphere(tuple(self.earth_center), radius=distance)

            #Condition: If x, y is on the "dark" side of the earth, get some different x, y
            #TODO update this with a "GOOD" function limiting the position, not too far back behind earth
            if y < 0:
                is_on_brightside = True

        set_location_bpy_object(self.camera_name, x, y, z)  
        self.x, self.y, self.z = x, y, z    
        
        self.set_camera_matrices()

    def randomize_camera_rotation(self):
        #3. Rotate the camera so within a limit of its field of view that still can capture part of the earth 
        # _, _, tangent_point = get_random_tangent_point_between_point_n_sphere(center=self.earth_center, radius=self.earth_radius, given_point=(x, y, z))
        random_directing_point = get_random_point_within_intersecting_tangent_circle_between_point_n_sphere(sphere_center=self.earth_center, sphere_radius=self.earth_radius, given_point=(self.x, self.y, self.z))
        rx, ry, rz = get_cam_angle_to_look_at(self.camera_name, random_directing_point)
        rx, ry, rz = radians(rx), radians(ry), radians(rz)
        
        set_rotation_euler_bpy_object(self.camera_name, rx, ry, rz)
        self.rx, self.ry, self.rz = rx, ry, rz
        
        self.set_camera_matrices()

    def randomize_camera_roll(self):
        #Rolling camera along its x-axis (outward axis)
        #https://blender.stackexchange.com/questions/78485/rotate-camera-using-eulers
        select_bpy_object(self.camera_name)
        roll_angle = random.uniform(0, 360)
        bpy.ops.transform.rotate(value=roll_angle, constraint_axis=(False, False, True), orient_type='LOCAL', mirror=False,  proportional_edit_falloff='SMOOTH', proportional_size=1)
        
        deselect_bpy_object()
        bpy.context.view_layer.update()

        self.rx, self.ry, self.rz = self.get_cam_rotation()

        self.set_camera_matrices()

    def point_camera_to_center_of_earth(self):
        angles = get_cam_angle_to_look_at(self.camera_name, self.earth_center)

        set_rotation_euler_bpy_object(self.camera_name, radians(angles[0]), radians(angles[1]), radians(angles[2]))
        self.rx, self.ry, self.rz = self.get_cam_rotation()
        self.set_camera_matrices()

    def create_camera(self, mode, creation_mode = 'create'):
        '''
        Create or import a camera. There should be only 1 camera
        Then define a random location of camera
        '''
        if creation_mode == "import":            
            if mode == 'full_earth':
                #randomize camera distance from earth surface
                self.randomize_camera_location()
                self.point_camera_to_center_of_earth()

            elif mode == 'empty_space_partial_earth':
                self.randomize_camera_location()

            else:
                raise ValueError(f'Not a valid mode {mode}')

            #Assuming the WIP blenderscene has already got a well setup camera, named "Camera" #TODO low priority, rename the object as Camera if name not Camera
            self.x, self.y, self.z, self.rx, self.ry, self.rz = get_bpy_camera_coordinates()

        elif creation_mode == 'create':
            self.delete_existing_cameras()
            #Only ever create 1 camera. Current camera must be deleted before making another one
            camera_data = bpy.data.cameras.new(name=self.camera_name)
            camera_object = bpy.data.objects.new(self.camera_name, camera_data)
            bpy.context.scene.collection.objects.link(camera_object)
            bpy.context.scene.camera = camera_object
            
            #Default position
            if mode == 'empty_space':
                self.x, self.y, self.z = 7.3589, -6.9258, 4.9583
                self.rx, self.ry, self.rz = radians(63.6), 0, radians(46.7)

            elif mode == 'empty_space_partial_earth':
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
        
        #Set depth of view to capture the furthest space target
        set_dof_distance(self.camera_name, self.st_range['depth'][-1] + 10) #Extra 10 meters
        self.set_camera_matrices()

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

    def set_camera_matrices(self):
        #Needs to be updated everytime the location or rotation of camera changes
        self.set_extrinsic_matrix()
        self.set_intrinsic_matrix()
    
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