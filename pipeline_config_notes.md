There are configerations with range and limits for simulations that has been tested and thus are constant until further experimentation
I. Camera
- We utilize default camera when started a blender(2.82) session
- Space targets should fall within the field of view of such camera
    depth: (8, 100) #Space targets should be 8 to 100 meters from the camera, in the camera coordinates
    horizontal_dist: (2.5, 36)   # x should be within this range
    vertical_dist: (1, 20)       # y

* For empty space background, camera is placed in the default position:
    self.x, self.y, self.z = 7.3589, -6.9258, 4.9583
    self.rx, self.ry, self.rz = radians(63.6), 0, radians(46.7)

II. Light:
- We use the type SUN for light
* For empty space background, light is placed in the default position:
    self.x, self.y, self.z = 4,1,6
    self.rx, self.ry, self.rz = radians(37.3), radians(3.16), radians(107)
    specular = 0.3
    angle = radians(40)
    strength = 40 

II. Earth:
1. For planet_earth_v1:
camera:
    self.x, self.y, self.z = 3.0638, -8.9029, -2.1132
    self.rx, self.ry, self.rz = radians(89.6), radians(0), radians(89.6)

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
* full_earth sky background
camera: 
        self.y runs from -900 to -1800
        self.x, self.y, self.z = 0, -900, 0
        self.rx, self.ry, self.rz = radians(90), radians(90), radians(0)
* partial earth
    camera:
        x, y, z orbits around earth from range #TODO
        rx, ry, rz: rotates around earth in range #TODO

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





