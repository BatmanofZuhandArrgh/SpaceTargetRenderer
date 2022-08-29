import random
from pprint import pprint 

from bpy_utils import append_bpy_object

class BackgroundGenerator():
    def __init__(self, config_dict) -> None:
        pprint(config_dict)
        self.all_modes = config_dict['modes']
        self.mode = random.choice(self.all_modes)

        ####TODO delete this:
        self.mode = "empty_space_partial_earth"
        print(f'Creating a(n) {self.mode} background') 

        self.earth_dict = config_dict['assets']['earth_blend']
        self.sky_dict   = config_dict['assets']['sky_blend']   

    def generate(self):
        #TODO paint background black by default, far-away stars' light is too faint to be captured by camera
        if self.mode == 'empty_space':
            return
        elif self.mode == 'empty_space_partial_earth':
            creation_mode = self.earth_dict['creation_mode']
            self.generate_earth(creation_mode)
        elif self.mode == 'full_earth':
            creation_mode = self.sky_dict['creation_mode']
            self.generate_sky(creation_mode)

    def generate_sky(self, creation_mode):
        #TODO generate sky
        pass

    def generate_earth(self, creation_mode):
        if creation_mode == 'create':
            self.create_earth()
        elif creation_mode == 'import':
            self.import_earth()

    def create_earth(self):
        #TODO create 3D earth from scratch if neccessary
        raise NotImplementedError()

    def import_earth(self):
        append_bpy_object(
            object= self.earth_dict['import_object'],
            section="Object",
            blend_filepath=self.earth_dict['import_blend']
        )

    def rotate(self):

        pass

def main():
    sample_config_dict = \
        {
            'modes': [
                'empty_space',
                'empty_space_partial_earth',
                'full_earth'
                ], 
            'assets':
            {
                'earth_blend': {
                    'import_object': "Earth",
                    'import_blend': "./asset/background/earth/planet_earth.blend",
                    'dir': './asset/background/earth', 
                    'earth_texture': './asset/background/sky/earth_texture', 
                    'cloud_texture': './asset/background/sky/cloud_texture',
                    'creation_mode': 'import',
                    }, 
                'sky_blend': {
                    'dir': './asset/background/sky', 
                    'sky_texture': './asset/background/sky/sky_texture',
                    'creation_mode': 'create',
                }
            }
        }
    background_gen = BackgroundGenerator(sample_config_dict)
    background_gen.generate()


if __name__ == '__main__':
    main()