import math
import numpy as np
from space_target import SpaceTarget

class CubeSat(SpaceTarget):
    def __init__(self, obj_name, img_coord, cam_coord, world_coord):
        super().__init__(obj_name, img_coord, cam_coord, world_coord)

        #init world coordinates of cubesat that are not rotated (rotation = 0,0,0) or translated (location = 0,0,0), we call this trivial
        #All cubesats vertices are equidistance from the center. It's also the max distance of any point in the cubesat to the center
        self.max_dist = math.sqrt(self.dimensions[0]**2 + self.dimensions[1]**2 + self.dimensions[2]**2)
        
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

    def update_vertices(self, cam_intrinsic_mat, cam_extrinsic_mat):
        vert_coords_world = [np.concatenate((ver, np.array([1])), axis = 0) for ver in self.vertices_coords_world]
        vert_coords_cam   = [cam_extrinsic_mat.dot(ver) for ver in vert_coords_world]
        vert_coords_img   = [cam_intrinsic_mat.dot(ver[:-1]) for ver in vert_coords_cam]
        self.vertices_coords_img  = [(ver/ver[-1]).astype(int)[:-1] for ver in vert_coords_img]

    def update_bbox(self, cam_intrinsic_mat, cam_extrinsic_mat):
        self.update_vertices(cam_intrinsic_mat, cam_extrinsic_mat)
        xs = [ver[0] for ver in self.vertices_coords_img]
        ys = [ver[1] for ver in self.vertices_coords_img]
        upper_left = (min(xs), min(ys))
        bottom_right = (max(xs), max(ys))
        self.bbox = (upper_left, bottom_right)