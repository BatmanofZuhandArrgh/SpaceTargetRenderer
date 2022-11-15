import glob as glob
from pprint import pprint
from render import RenderPipeline
from utils.utils import get_yaml, dump_yaml


def main():

    config_paths = glob.glob('./*.yaml')
    for config_path in config_paths:
        config = get_yaml(config_path=config_path)
        pprint(config)
    #     pipeline = RenderPipeline(config_path=config_path)

    #     pipeline.render()

if __name__ == '__main__':
    main()