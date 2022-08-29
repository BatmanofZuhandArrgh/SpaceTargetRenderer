import bpy
from bpy_utils import delete_bpy_object, move_bpy_object, select_bpy_object, select_bpy_object, set_location_bpy_object 

class CameraGenerator():
    def __init__(self, config_dict) -> None:
        #By default
        self.config_dict = config_dict

    def delete_existing_cameras(self):
        # Delete all existing cameras
        existing_cameras = [ob for ob in list(bpy.context.scene.objects) if ob.type == 'CAMERA']
        for camera in existing_cameras:
            camera_name = camera.name
            delete_bpy_object(camera_name)

    def create_camera(self):
        camera_name = "Camera"
        #Only ever create 1 camera. Current camera must be deleted before making another one
        camera_data = bpy.data.cameras.new(name=camera_name)
        camera_object = bpy.data.objects.new(camera_name, camera_data)
        bpy.context.scene.collection.objects.link(camera_object)
        set_location_bpy_object(camera_name, x, y ,z)

    def setup(self):
        self.delete_existing_cameras()
        self.create_camera()
        self.move_camera()
    
    def move_camera(self, x_offset, y_offset, z_offset):
        # By default there should only be 1 camera named "Camera"
        move_bpy_object("Camera", x_offset, y_offset, z_offset)

def main():
    pass

if __name__ == '__main__':
    main()