from importlib.resources import path
import os
import yaml
import random
import glob

from ast import literal_eval
from pprint import pprint

from bpy_utils import append_bpy_object

IMG_EXT = ['.jpg', '.jpeg', '.png']
class SpaceTargetGenerator():
    def __init__(self, config_dict) -> None:
        # pprint(config_dict)
        
        self.cubesat_dict = config_dict['cubesats']
        self.other_st_dict= config_dict['other_st']
        self.other_dict = config_dict['other']
        self.range_num_obj = literal_eval(config_dict['range_num_obj'])
    
        self.space_targets_included = [st for st in config_dict.keys() if type(config_dict[st]) == dict and config_dict[st]['included']]

        #Creating dictionaries of other space targets and their textures
        self.space_targets = {}    
        for dictionary in [self.other_dict, self.other_st_dict]:
            if dictionary['included']:
                blend_paths = [path for path in glob.glob(f'{dictionary["dir"]}/**', recursive = True) if '.blend' in path]
                blend_names = [os.path.splitext(os.path.basename(path))[0] for path in blend_paths]
                for i, blend_name in enumerate(blend_names):
                    self.space_targets[blend_name] = {}
                    self.space_targets[blend_name]['dir'] = blend_paths[i]
                    self.space_targets[blend_name]['textures'] = [path for path in glob.glob(f'{dictionary["textures"]}/{blend_name}/**', recursive=True) if '.' + path.split('.')[-1].lower() in IMG_EXT]                    
        
        if self.cubesat_dict['included']:
            for key in self.cubesat_dict:
                if "U" in key:
                    self.space_targets[key] = {}
                    self.space_targets[key]['dir'] = self.cubesat_dict[key]
                    self.space_targets[key]['textures'] = [path for path in glob.glob(f'{self.cubesat_dict["textures"]}/**', recursive=True) if '.' + path.split('.')[-1].lower() in IMG_EXT]    

        pprint(self.space_targets)

    
    def generate(self):
        #By default, pipeline imports the space targets, instead of c
        num_obj = random.randrange(self.range_num_obj[0], self.range_num_obj[1])
        print(num_obj)

        for i in range(num_obj):
            #append_bpy_object()
            pass

def main():
    with open('pipeline_config.yaml', "r") as stream:
            try:
                config_dict = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    st_dict = config_dict['space_targets']
    space_target_generator = SpaceTargetGenerator(st_dict)
    space_target_generator.generate()
    pass

if __name__ == "__main__":
    main()

