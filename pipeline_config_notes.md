PATHS:
- blender_exe: Path to blender executable file
- blender_engine: String of the rendering engine, either BLENDER_EEVEE or CYCLES
- output_dir: Path to the output
- label_dict: Path to label mapping yaml files, see ./annotations
- WIP_blend_file_path: Leave empty

There are configerations with range and limits for simulations that has been tested and thus are constant until further experimentation

- img_size: size of images of the output dataset
- modes: background modes, empty_space_partial_earth, empty_space and/or full_earth (see paper.pdf for more details)

I. Background
earth_blend: A blend file with Earth model, camera and lighting set up. When the background mode is full_earth or empty_space_partial_earth, that blend file is opened and used to generate images. For each background mode, camera and light are set up with different configurations.

- creation_mode: import (create mode is not implemented)

1. For planet_earth_v1:
light: 
    self.x, self.y, self.z = 0,0,0
    self.rx, self.ry, self.rz = radians(90), radians(90), 0
    specular = 0
    angle = radians(0.5)
    strength = 10

earth:
    x, y, z = 0,0,0
    earth dimensions = 15.8, 15.8, 15.8
    cloud dimensions = 15.8, 15.8, 16

2. For planet_earth_v2:
light:
    self.x, self.y, self.z = 0,0,0
    self.rx, self.ry, self.rz = radians(90), radians(90), 0
    specular = 0
    angle = radians(0.5)
    strength = 10

earth: 
    x, y, z = 0,0,0
    earth dimensions = 1274.2, 1274.2, 1274.2
    cloud dimensions = 1278, 1278, 1278

II. Light:
- We use the type SUN for light
* For empty space background, light is placed in the default position:
    self.x, self.y, self.z = 4,1,6
    self.rx, self.ry, self.rz = radians(37.3), radians(3.16), radians(107)
    specular = 0.3
    angle = radians(40)
    strength = 40 


III. Camera
- We utilize default camera when started a blender(2.82) session
- Space targets should fall within the field of view of such camera
    depth: (8, 100) #Space targets should be 8 to 100 meters from the camera, in the camera coordinates
    horizontal_dist: (2.5, 36)   # x should be within this range
    vertical_dist: (1, 20)       # y

    cam2earth_range:
        distance: ranges from closest to center to furthest

* For empty space background, camera is placed in the default position:
    self.x, self.y, self.z = 7.3589, -6.9258, 4.9583
    self.rx, self.ry, self.rz = radians(63.6), 0, radians(46.7)

IV. Space targets:
space_targets:
    range_num_obj: ranges from the minimum to maximum number of objs per img

V. Operation_config:
- See RenderingPipelineFlowchart to see definition of cycles, iterations and views. The number of loops can be modified here












