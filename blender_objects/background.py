import yaml

from pprint import pprint 

from utils.bpy_utils import append_bpy_object, change_background_color

class BackgroundGenerator():
    def __init__(self, config_dict) -> None:

        self.earth_dict = config_dict['assets']['earth_blend']
        self.sky_dict   = config_dict['assets']['sky_blend']   

    def generate(self, mode):
        #Space background color: pitch black
        change_background_color()
        
        print(f'Creating a(n) {mode} background')

        if mode == 'empty_space':
            return "", 'create'
        elif mode == 'empty_space_partial_earth':
            creation_mode = self.earth_dict['creation_mode']
            return self.generate_earth(creation_mode), creation_mode
        elif mode == 'full_earth':
            creation_mode = self.sky_dict['creation_mode']
            return self.generate_sky(creation_mode), creation_mode

    def generate_sky(self, creation_mode):
        #TODO generate sky
        pass

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
    with open('pipeline_config.yaml', "r") as stream:
        try:
            config_dict = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    
    bg_dict = config_dict['background']
    background_gen = BackgroundGenerator(bg_dict)
    background_gen.generate('create')


if __name__ == '__main__':
    main()