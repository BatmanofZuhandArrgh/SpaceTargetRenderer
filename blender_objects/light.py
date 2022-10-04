import bpy
from math import radians
from ast import literal_eval

from utils.bpy_utils import delete_bpy_object, set_location_bpy_object, set_rotation_euler_bpy_object, get_bpy_sun_coordinates

class LightGenerator():
    def __init__(self, config_dict) -> None:
        self.config_dict = config_dict

        self.x, self.y, self.z = None, None, None
        self.rx, self.ry, self.rz = None, None, None
    
    def delete_existing_light(self): 
        existing_lights = [ob for ob in list(bpy.context.scene.objects) if ob.type == 'LIGHT']
        for light in existing_lights:
            light_name = light.name
            delete_bpy_object(light_name)

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
            return

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
            self.rx, self.ry, self.rz=literal_eval(self.config_dict['rotation'])
        
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
            self.rx, self.ry, self.rz = radians(63.6), 0, radians(46.7)
            specular = None
            angle = None
            strength = None
        
        bpy.ops.object.light_add(type=type, radius=radius)
        #already linked to collection
        light_obj = bpy.context.active_object
        light = light_obj.data
        light.name = type[0].upper() + type[1:].lower()
        light.angle = angle
        light.energy = strength
        light.specular_factor = specular
        
        set_location_bpy_object(light.name, self.x, self.y,self.z)
        set_rotation_euler_bpy_object(light.name, self.rx, self.ry, self.rz)


def main():
    pass

if __name__ == "__main__":
    main()
        
