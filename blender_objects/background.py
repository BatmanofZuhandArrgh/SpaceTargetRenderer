import os
import random

from pprint import pprint 

from utils.bpy_utils import replace_img_texture, random_rotate_bpy_object, set_bloom
from utils.img_utils import IMG_EXT
from utils.utils import get_yaml

class BackgroundGenerator():
    def __init__(self, config_dict) -> None:

        self.earth_dict = config_dict['assets']['earth_blend']
        # self.sky_dict   = config_dict['assets']['sky_blend']   

    def generate(self, mode):
        print(f'Creating a(n) {mode} background')

        if mode == 'empty_space':
            return "", 'create'
        elif mode == 'empty_space_partial_earth':
            creation_mode = self.earth_dict['creation_mode']
            return self.generate_earth(creation_mode), creation_mode

    def replace_cloud(self):
        cloud_texture_paths = [path for path in os.listdir(self.earth_dict['cloud_texture']) if '.'+path.split('.')[-1].lower() in IMG_EXT]
        new_cloud_texture_path = os.path.join(self.earth_dict['cloud_texture'], random.choice(cloud_texture_paths))

        replace_img_texture(
            obj_name="Cloud", 
            image_path = new_cloud_texture_path, 
            )
    
    def rotate_cloud(self):
        random_rotate_bpy_object("Cloud")

    def rotate_earth(self):
        random_rotate_bpy_object("Earth")

    def modify_earth(self):
        self.rotate_cloud()
        self.rotate_earth()

    def randomize_bloom():
        set_bloom(
            # bloom_radius=0,
            bloom_threshold= random.uniform(0,1),
            # bloom_color=,
        )

    def generate_earth(self, creation_mode):
        if creation_mode == 'create':
            return self.create_earth()
        elif creation_mode == 'import':
            # Possibly return WIP blend path
            return self.import_earth()

    def create_earth(self):
        #TODO create 3D earth from scratch if neccessary
        raise NotImplementedError()

    def import_earth(self):
        '''
        Output a path to existing input blend file to start from there (Does not actually import separate parts of earth)        
        '''
        #Instead of putting earth from existing blend
        # append_bpy_object(
            # object= self.earth_dict['import_object'],
            # section="Object",
        #     # blend_filepath=self.earth_dict['import_blend']
        # )

        # We would use the existing blend as the WIP starting blend
        # Return Earth asset file path as the WIP file_path
        return self.earth_dict['import_blend']
        
    def rotate(self):
        pass

def main():
    config_dict = get_yaml('pipeline_config.yaml')
    
    bg_dict = config_dict['background']
    background_gen = BackgroundGenerator(bg_dict)
    background_gen.generate('create')


if __name__ == '__main__':
    main()