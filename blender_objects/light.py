import bpy
from math import radians
from ast import literal_eval

from bpy_utils import delete_bpy_object

class LightGenerator():
    def __init__(self, config_dict) -> None:
        self.config_dict = config_dict
        self.mode = None
    
    def delete_existing_light(self): 
        existing_lights = [ob for ob in list(bpy.context.scene.objects) if ob.type == 'LIGHT']
        for light in existing_lights:
            light_name = light.name
            delete_bpy_object(light_name)

    def create_light(self, type = 'SUN', angle = 40, strength = 40, radius = 1, location = (0,0,16)):
        bpy.ops.object.light_add(type=type, radius=radius, location=location)

        light_obj = bpy.context.active_object
        light = light_obj.data
        light.name = type[0].upper() + type[1:].lower()
        light.angle = radians(angle)
        light.energy = strength
        # bpy.context.collection.objects.link(light_obj)
    
    def setup(self):
        self.delete_existing_light()
        self.create_light(
            type=self.config_dict['type'],
            angle=self.config_dict['angle'],
            strength=self.config_dict['strength'],
            radius=self.config_dict['radius'],
            location=literal_eval(self.config_dict['location'])
        )

    def positioning(self):
        pass

    def generate(self, mode, creation_mode):
        if creation_mode == 'import':
            #Assume any WIP blend would already have light source
            return

        self.mode = mode
        self.setup()
        self.positioning()

def main():
    pass

if __name__ == "__main__":
    main()
        
