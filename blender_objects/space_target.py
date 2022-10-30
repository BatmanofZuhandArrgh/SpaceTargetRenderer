import numpy as np

from utils.bpy_utils import get_dimensions_bpy_object, get_rotation_euler_bpy_object
class SpaceTarget():
    def __init__(
        self, obj_name, img_coord, cam_coord, world_coord
    ):  
        self.obj_name = obj_name
        self.img_coord = img_coord
        self.cam_coord = cam_coord
        self.world_coord = world_coord
        self.obj_type = 'cubesat' if '_CubeSat' in obj_name else 'other_st'
        self.cls_type = obj_name.split('_')[2].lower() if self.obj_type == 'cubesat' else 'other_st'
        self.rotation = (0,0,0)
        self.location = world_coord
        self.dimensions = np.array(get_dimensions_bpy_object(obj_name))
        # self.diagonal   = sqrt(self.dimensions[0]**2 + self.dimensions[1]**2 + self.dimensions[2]**2)

        self.bbox = None #tuple of start point and end point. THose points are tuples of (x_min, y_min), (x_max, y_max)

    def update(self, world_coord = None, cam_coord = None, img_coord = None):
        '''
        If new parameters' values are input, spacetarget params are updated.
        If not and the function is called, only the rotation is updated
        '''
        self.img_coord = img_coord if img_coord is not None else self.img_coord
        self.cam_coord = cam_coord if cam_coord is not None else self.cam_coord
        self.world_coord = world_coord if world_coord is not None else self.world_coord
        self.rotation = np.array(get_rotation_euler_bpy_object(self.obj_name))
        self.location = self.world_coord

    def print_info(self):
        print(f'Name: {self.obj_name}')
        print('world, cam, img coords: ', self.world_coord, self.cam_coord, self.img_coord)
        print('rotation, location: ', self.rotation, self.location)
        print('dimensions: ', self.dimensions)
        # print('vertices: ', self.vertices_coords_world, self.vertices_coords_img)
