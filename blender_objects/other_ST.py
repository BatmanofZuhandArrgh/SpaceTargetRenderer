import os
import numpy as np
import bpy
from mathutils import Vector

from blender_objects.cubesat import CubeSat

from utils.bpy_utils import get_dimensions_bpy_object, select_bpy_object, deselect_bpy_object

#Depreciated, not needed as of now
#Can be extended if needed
class Other_ST(CubeSat):
    def __init__(self, obj_name, img_coord, cam_coord, world_coord):
        super().__init__(obj_name, img_coord, cam_coord, world_coord)
        
        self.stretch_obj()
        obj = bpy.data.objects[self.obj_name]
    
        self.vertices_coords_world_trivial = [np.asarray(v[:]) * self.scale_ratios for v in obj.bound_box]

    def stretch_obj(self):
        #Scale cuz the ot_sts are sometimes too small or too big

        obj = bpy.data.objects[self.obj_name]

        obj_dimension = np.array(obj.dimensions)
        min_scale_ratio = 2 / min(obj_dimension) # 2m is the dimension of a default cube in blender
        self.scale_ratios = np.array([np.random.uniform(min_scale_ratio, 2*min_scale_ratio), np.random.uniform(min_scale_ratio, 2*min_scale_ratio), np.random.uniform(min_scale_ratio, 2*min_scale_ratio)])
        obj.dimensions = (obj_dimension[0]* self.scale_ratios[0], obj_dimension[1]* self.scale_ratios[1], obj_dimension[2]* self.scale_ratios[2])

        bpy.context.view_layer.update()
        self.dimensions = np.array(get_dimensions_bpy_object(self.obj_name))