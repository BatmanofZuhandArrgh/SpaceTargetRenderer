import numpy as np

from blender_objects.space_target import SpaceTarget
from utils.math_utils import get_rotation_mat

#For the moment, to map bounding box, this flow works with both CubeSat and Other_SpaceTargets
# It will output not tight, but good enough bounding box for other st
class CubeSat(SpaceTarget):
    def __init__(self, obj_name, img_coord, cam_coord, world_coord):
        super().__init__(obj_name, img_coord, cam_coord, world_coord)

        #init world coordinates of cubesat that are not rotated (rotation = 0,0,0) or translated (location = 0,0,0), we call this trivial
        #All cubesats vertices are equidistance from the center. It's also the max distance of any point in the cubesat to the center
        # self.max_dist = math.sqrt(self.dimensions[0]**2 + self.dimensions[1]**2 + self.dimensions[2]**2)
        
        world_abs_vertex_coord = self.dimensions/2 #Absolute values of vertices in non-rotated non-translated cubesats
        world_vertix_multiplier = [
            [1,1,1],
            [1,1,-1],
            [1,-1,1],
            [-1,1,1],
            [-1,-1,1],
            [1,-1,-1],
            [-1,1,-1],
            [-1,-1,-1],
        ]
        self.vertices_coords_world_trivial = [ver* world_abs_vertex_coord for ver in world_vertix_multiplier] #world coords of vertices when it's trivial
        self.vertices_coords_world = None #world coords of vertices when taken into account rotation and translation in rendering (after self.update())
        self.vertices_coords_img   = None #img coords of vertices when transformed with camera matrices (after self.update_vertices())

    def update(self, world_coord = None, cam_coord = None, img_coord = None):
        super().update(world_coord, cam_coord, img_coord)
        rotation_mat = get_rotation_mat(self.rotation[0],self.rotation[1], self.rotation[2])
        self.vertices_coords_world = [self.location + rotation_mat.dot(vert) for vert in self.vertices_coords_world_trivial]

    def update_vertices(self, cam_intrinsic_mat, cam_extrinsic_mat):
        #Convert vertices from world coordinates to camera coordinates, then to img coords
        vert_coords_world = [np.concatenate((ver, np.array([1])), axis = 0) for ver in self.vertices_coords_world]
        vert_coords_cam   = [cam_extrinsic_mat.dot(ver) for ver in vert_coords_world]
        vert_coords_img   = [cam_intrinsic_mat.dot(ver[:-1]) for ver in vert_coords_cam]
        self.vertices_coords_img  = [(ver/ver[-1]).astype(int)[:-1] for ver in vert_coords_img]

    def update_bbox(self, cam_intrinsic_mat, cam_extrinsic_mat, img_size):
        img_width, img_height = img_size
        self.update_vertices(cam_intrinsic_mat, cam_extrinsic_mat)
        xs = [ver[0] for ver in self.vertices_coords_img]
        ys = [ver[1] for ver in self.vertices_coords_img]
        upper_left = ( max(0, min(xs)), max(0, min(ys)))
        bottom_right = ( min(img_width - 1, max(xs)), min(img_height - 1, max(ys)))
        self.bbox = (upper_left, bottom_right)