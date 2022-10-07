import os

from space_target import SpaceTarget

class Other_ST(SpaceTarget):
    def __init__(self, obj_name, img_coord, cam_coord, world_coord):
        super().__init__(obj_name, img_coord, cam_coord, world_coord)
        self.bbox = ((0,0),(0,0))
        
    def update_bbox(self,cam_intrinsic_mat, cam_extrinsic_mat):
        pass
    