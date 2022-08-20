import random

class BackgroundGenerator():
    def __init__(self, config_dict) -> None:
        self.all_modes = config_dict['modes']
        self.mode = random.choice(self.modes)
        print(f'Creating a(n) {self.mode} background') 

        self.earth_dict = config_dict['earth_blend']
        self.sky_dict   = config_dict['sky_blend']   

    def generate(self):
        #TODO paint background black by default, far-away stars' light is too faint to be captured by camera
        if self.mode == 'empty_space':
            return
        elif self.mode == 'empty_space_partial_earth':
            creation_mode = self.earth_dict['creation_mode']
        elif self.mode == 'full_earth':
            creation_mode = self.sky_dict['creation_mode']
        
        self.generate_earth(creation_mode)

    def generate_earth(self, creation_mode):
        if creation_mode == 'create':
            self.create_earth()
        elif creation_mode == 'import':

    def create_earth(self):
        #TODO create 3D earth from scratch if neccessary
        raise NotImplementedError()
        

    def rotate(self):

        pass

def main():
    sample_config_dict = \
        {
            'modes': ['empty_space', 'empty_space_partial_earth', 'full_earth'], 
            'earth_blend': {
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
    background_gen = BackgroundGenerator(sample_config_dict)



if __name__ == '__main__':
    main()