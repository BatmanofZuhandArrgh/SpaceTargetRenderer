import bpy

from math import radians
from bpy_utils import delete_bpy_object, move_bpy_object,\
     select_bpy_object, select_bpy_object,\
         set_location_bpy_object, set_rotation_euler_bpy_object 

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

    def create_camera(self, mode, creation_mode):
        if creation_mode == "import":
            #Assuming the WIP blenderscene has already got a well setup camera, named "Camera"
            return

        self.delete_existing_cameras()
        camera_name = "Camera"
        #Only ever create 1 camera. Current camera must be deleted before making another one
        camera_data = bpy.data.cameras.new(name=camera_name)
        camera_object = bpy.data.objects.new(camera_name, camera_data)
        bpy.context.scene.collection.objects.link(camera_object)
        bpy.context.scene.camera = camera_object

        if mode == 'empty_space':
            x, y, z = 7.3589, -6.9258, 4.9583
            rx, ry, rz = radians(63.6), 0, radians(46.7)

        elif mode == 'empty_space_partial_earth':
            #TODO edit general camera positioning
            x, y, z = 3.0638, -8.9029, -2.1132
            rx, ry, rz = radians(89.6), radians(0), radians(89.6)

        elif mode == "full_earth":
            x, y, z = 0, 0, 0
            rx, ry, rz = 0, 0, 0

        set_location_bpy_object(camera_name, x, y, z)
        set_rotation_euler_bpy_object(camera_name, rx, ry, rz)

    def setup(self, mode, creation_mode):
        self.create_camera(mode, creation_mode)
    
    def move_camera(self, x_offset, y_offset, z_offset):
        # By default there should only be 1 camera named "Camera"
        move_bpy_object("Camera", x_offset, y_offset, z_offset)
    
    def get_camera_coordinates(self):
        camera = bpy.context.scene.camera
        return camera.location.x, camera.location.y, camera.location.z, \
            camera.rotation_euler.x, camera.rotation_euler.y, camera.rotation_euler.z

def main():
    pass

if __name__ == '__main__':
    main()