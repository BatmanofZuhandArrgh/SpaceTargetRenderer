import bpy
import numpy as np
from math import radians
from ast import literal_eval

from utils.bpy_utils import delete_bpy_object, set_location_bpy_object, set_rotation_euler_bpy_object, get_bpy_sun_coordinates

class LightGenerator():
    def __init__(self, config_dict) -> None:
        self.config_dict = config_dict

        self.x, self.y, self.z = None, None, None
        self.rx, self.ry, self.rz = None, None, None
        self.light_name = config_dict['light_name']
        self.strength_range = None 
    
    def delete_existing_light(self): 
        existing_lights = [ob for ob in list(bpy.context.scene.objects) if ob.type == 'LIGHT']
        for light in existing_lights:
            light_name = light.name
            delete_bpy_object(light_name)
    
    def randomize_light_strength(self, mode):
        light_obj = bpy.data.objects[self.light_name]
        light_data = light_obj.data

        if mode == 'empty_space':
            self.strength_range = (1, 60)
        elif mode in ['full_earth', 'empty_space_partial_earth']:
            self.strength_range = (1, 20)
        
        light_data.energy = np.random.uniform(low=self.strength_range[0], high=self.strength_range[1], size=None)

    def create_light(
        self, 
        mode,
        creation_mode = 'import'
    ):
        '''
        Create or import light. There should be only one 
        '''
        if creation_mode == 'import':
            self.x, self.y, self.z, self.rx, self.ry, self.rz = \
                get_bpy_sun_coordinates()
        elif creation_mode == 'create':

            self.delete_existing_light()   

            type = 'SUN'
            angle = 40
            strength = 40 
            radius = 1
            
            if self.config_dict['specify_config']:
                type=self.config_dict['type']
                angle=self.config_dict['angle']
                strength=self.config_dict['strength'],
                radius=self.config_dict['radius'],
                self.x, self.y, self.z=literal_eval(self.config_dict['location'])
                
                rotations = literal_eval(self.config_dict['rotation'])
                self.rx, self.ry, self.rz= radians(rotations[0]),radians(rotations[1]),radians(rotations[2])

            elif mode == 'empty_space':
                self.x, self.y, self.z = 4,1,6
                self.rx, self.ry, self.rz = radians(37.3), radians(3.16), radians(107)
                specular = 0.3
                angle = radians(40)
                strength = 40 

            elif mode == 'empty_space_partial_earth':
                self.x, self.y, self.z = 0,0,0
                self.rx, self.ry, self.rz = radians(90), radians(90), 0
                specular = 0
                angle = radians(0.5)
                strength = 10

            elif mode == 'full_earth':
                self.x, self.y, self.z = 0,0,0
                self.rx, self.ry, self.rz = radians(90), radians(90), 0
                specular = 0
                angle = radians(0.5)
                strength = 10

            bpy.ops.object.light_add(type=type, radius=radius)
            #already linked to collection
            light_obj = bpy.context.active_object
            light = light_obj.data
            light.name = self.light_name
            light.angle = angle
            light.energy = strength
            light.specular_factor = specular
            
            set_location_bpy_object(light.name, self.x, self.y,self.z)
            set_rotation_euler_bpy_object(light.name, self.rx, self.ry, self.rz)
        else:
            return ValueError(f'Not a valid creation mode {creation_mode}')

def main():
    pass

if __name__ == "__main__":
    main()
        
