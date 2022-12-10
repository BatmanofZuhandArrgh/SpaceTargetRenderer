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
    
        self.vertices_coords_world_trivial = [np.asarray(v[:]) * np.array([self.scale_ratio,self.scale_ratio,self.scale_ratio]) for v in obj.bound_box]

    def stretch_obj(self):
        #Scale cuz the ot_sts are sometimes too small or too big

        obj = bpy.data.objects[self.obj_name]

        obj_dimension = np.array(obj.dimensions)
        self.scale_ratio = 2 / min(obj_dimension) # 2m is the dimension of a default cube in blender
        obj.dimensions = (obj_dimension[0]* self.scale_ratio, obj_dimension[1]* self.scale_ratio, obj_dimension[2]* self.scale_ratio)

        bpy.context.view_layer.update()
        self.dimensions = np.array(get_dimensions_bpy_object(self.obj_name))