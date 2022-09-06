from bpy_utils import add_light

class LightGenerator():
    def __init__(self, config_dict) -> None:
        self.config_dict = config_dict
        self.mode = None

    def setup(self):
        pass

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
        
