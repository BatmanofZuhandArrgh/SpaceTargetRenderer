import os

from blender_objects.space_target_gen import SpaceTarget

#Depreciated, not needed as of now
#Can be extended if needed
class Other_ST(SpaceTarget):
    def __init__(self, obj_name, img_coord, cam_coord, world_coord):
        super().__init__(obj_name, img_coord, cam_coord, world_coord)

    def update_bbox(self,cam_intrinsic_mat, cam_extrinsic_mat):
        raise NotImplementedError
    