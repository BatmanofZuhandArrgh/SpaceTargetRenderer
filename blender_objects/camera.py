import bpy
import numpy as np

from ast import literal_eval

from utils.math_utils import get_random_point_on_3dpolygon, get_random_point_on_3dline
np.set_printoptions(suppress=True)

from math import radians, cos, sin
from utils.bpy_utils import delete_bpy_object, move_bpy_object,\
     select_bpy_object, select_bpy_object,\
         set_location_bpy_object, set_rotation_euler_bpy_object,\
            rotate_bpy_object

class CameraGenerator():
    def __init__(self, config_dict) -> None:
        #By default
        self.config_dict = config_dict

        self.x, self.y, self.z = None, None, None
        self.rx, self.ry, self.rz = None, None, None
        
        self.extrinsic_matrix = None
        self.intrinsic_matrix = None

        self.inv_extrinsic_matrix = None
        self.inv_intrinsic_matrix = None

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
                self.get_bpy_camera_coordinates()
            
            self.set_extrinsic_matrix()
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
        extrinsic_matrix_rx = np.array([1, 0, 0, 0, cos(self.rx), -sin(self.rx), 0, sin(self.rx), cos(self.rx)]).reshape(3,3)
        extrinsic_matrix_ry = np.array([cos(self.ry), 0, sin(self.ry), 0, 1, 0, -sin(self.ry), 0, cos(self.ry)]).reshape(3,3)
        extrinsic_matrix_rz = np.array([cos(self.rz),-sin(self.rz), 0, sin(self.rz), cos(self.rz), 0, 0, 0, 1]).reshape(3,3)

        extrinsic_matrix_t = np.array([self.x, self.y, self.z]).reshape(3,1)
                
        rotation_matrix = extrinsic_matrix_rx.dot(extrinsic_matrix_ry).dot(extrinsic_matrix_rz)

        rotation_matrix = np.concatenate((rotation_matrix, np.zeros(shape=(1, 3))), axis = 0) #(3*4)
        
        translation_matrix = np.concatenate((extrinsic_matrix_t, np.array([[1]])), axis = 0) #(3*1)
        
        self.extrinsic_matrix = np.concatenate((rotation_matrix, translation_matrix), axis=1)
        self.inv_extrinsic_matrix = np.linalg.inv(self.extrinsic_matrix)
        
    def set_intrinsic_matrix(self):
        pass

    def get_extrinsic_matrix(self):
        return self.extrinsic_matrix
    
    def get_intrinsic_matrix(self):
        return self.intrinsic_matrix

    def move_camera(self, x_offset, y_offset, z_offset):
        # By default there should only be 1 camera named "Camera"
        move_bpy_object("Camera", x_offset, y_offset, z_offset)
    
    def get_bpy_camera_coordinates(self):
        #Get location and rotation from bpy camera object, when not set by CamGen
        camera = bpy.context.scene.camera
        return camera.location.x, camera.location.y, camera.location.z, \
            camera.rotation_euler.x, camera.rotation_euler.y, camera.rotation_euler.z
    
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
        points_worldCoord = [coord[:-1].astype(int) for coord in points_worldCoord]
        
        return points_worldCoord

def main():
    import yaml
    config_path = './pipeline_config.yaml'
    with open(config_path, "r") as stream:
        try:
            config_dict = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

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