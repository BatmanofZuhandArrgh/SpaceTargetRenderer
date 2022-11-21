import random
import numpy as np
import matplotlib.pyplot as plt

from math import radians, cos, sin, sqrt

def degrees(radian):
    return radian * 180 / np.pi
    
def matrix_rotate_by_90(a):
    a.reverse()
    for i in range(len(a)):
        for j in range(i): 
            a[i][j], a[j][i] = a[j][i], a[i][j]
    return a

def get_random_rotation_offset():
    return radians(random.uniform(0, 180))

def get_x_rotation_mat(angle):
    return np.array([
        [1,0,0],
        [0, cos(angle), -sin(angle)],
        [0, sin(angle),  cos(angle)]
    ])

def get_y_rotation_mat(angle):
    return np.array([
        [ cos(angle), 0, sin(angle)],
        [0, 1, 0],
        [-sin(angle), 0, cos(angle)]
    ])

def get_z_rotation_mat(angle):
    return np.array([
        [cos(angle), -sin(angle), 0],
        [sin(angle),  cos(angle), 0],
        [0,0,1]
    ])

def get_rotation_mat(x_angle, y_angle, z_angle):
    x_mat = get_x_rotation_mat(x_angle)
    y_mat = get_y_rotation_mat(y_angle)
    z_mat = get_z_rotation_mat(z_angle)
    return (z_mat.dot(y_mat)).dot(x_mat)

def get_random_point_on_3dpolygon(max_abs_x, max_abs_y, z_coord, num_points):
    '''
    Generate random shapely points on a polygon parallel to camera lense surface
    The 3d polygon is a rectangle that share the same perpendicular axis with he camera lense polygon,
    defined with height = 2*max_abs_y, width = 2*max_abs_y
    The point is uniformly randomlly picked from within this polygon
    The point is in the camera coordinates

    output: list of points as np array
    '''
    minx, maxx = -max_abs_x, max_abs_x
    miny, maxy = -max_abs_y, max_abs_y
    
    points = []
    for i in range(num_points):
        point = np.array([random.uniform(minx, maxx), random.uniform(miny, maxy), z_coord])
        points.append(point)
    
    return points

def get_3dline_equation(pointA, pointB):
    '''
    vector form equation of 3dline
    output: pointA as np array, dir vector as np array
    '''
    pointA, pointB = np.asarray(pointA), np.asarray(pointB)

    #direction vector t
    dir_vector = pointB - pointA
    #r(t) = pointA + t*dir_vector
    return pointA, dir_vector

def get_distance_between_2points(point1, point2):
    point1, point2 = np.asarray(point1), np.asarray(point2)
    return sqrt(sum(np.square(point1 - point2)))

def get_random_tangent_point_between_point_n_sphere(center, radius, given_point):
    '''
    See documentation section: #TODO add in, to see notation
    Set of all tangents point from a given point (outside of the sphere) to the sphere is a circle in the 3D space
    Return the center of that intersecting circle, radius of that circle, and a random tangent point on that circle 
    '''
    given_point, center= np.asarray(given_point), np.asarray(center)

    #1. Find distance between given point and center of the sphere
    d2 = get_distance_between_2points(np.array(given_point), np.array(center))
    #Distance between A (given point) to O(center of sphere)

    if d2 < radius:
        raise ValueError('Given point must be outside of the sphere')

    #2. Find the length of the tangent line segment from the point to the sphere surface
    d1 = sqrt(d2 **2 - radius**2)
    # It's the segment length between A (given point) to B(tangent point)

    #3. Find distance between B and OA, called BH with length r, BH is perpendicular to OA
    r = radius * d1 / d2
    # This will be the radius of the circle that is the intersection between (given sphere) and (sphere with given point A as center and d1 as radius)

    #4. Find distance between H and center O: called this h0
    h0 = radius **2 / d2

    #4. Find the location of point H
    center, dir_vector = get_3dline_equation(center, given_point)
    coord_H =  center + dir_vector * (h0/d2)

    #5. Define a plane that is perpendicular with OH at point H
    from skspatial.objects import Plane, Sphere, Line, Point
    ortho_plane = Plane(point=np.asarray(coord_H), normal=coord_H / h0)
    cartesian_coeffs = ortho_plane.cartesian()

    random_point_in_plane = get_random_point_on_3dplane(cartersian_coeffs=cartesian_coeffs)
    # print(random_point_in_plane)
    random_line_in_plane = Line.from_points(coord_H, np.asarray(random_point_in_plane))
    earth_sphere = Sphere(point=center, radius=radius)
    intersect_pt_a, intersect_pt_b = earth_sphere.intersect_line(random_line_in_plane)
    tangent_point = random.choice([intersect_pt_a, intersect_pt_b])

    #Visualize
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # ortho_plane.plot_3d(ax, alpha=0.2)
    # earth_sphere.plot_3d(ax, alpha=0.2)
    # tangent_point.plot_3d(ax, alpha = 0.2)
    # random_line_in_plane.plot_3d(ax, alpha = 0.2)
    # coord_H0 = get_point_further_than_tangent_point(coord_H, tangent_point, ratio = 1.3)
    # further_tangent_point = Point(coord_H0)
    # further_tangent_point.plot_3d(ax, alpha = 0.2)
    # plt.show()

    #Assure that the tangent is correct
    if abs(get_distance_between_2points(tangent_point, coord_H) - r) > 0.1:
        raise ValueError(get_distance_between_2points(tangent_point, coord_H), r)

    return coord_H, r, tangent_point    

def get_point_further_than_tangent_point(coord_H, tangent_point, ratio = 1.15):
    '''
    Return point further or closer to the circle center than the tangent point
    '''
    coord_H, dir_vector = get_3dline_equation(coord_H, tangent_point)
    coord_H0 =  coord_H + dir_vector * ratio
    return coord_H0

def get_random_point_within_intersecting_tangent_circle_between_point_n_sphere(sphere_center, sphere_radius, given_point, ratio_high = 1.4):
    circle_center, circle_radius, random_tangent_point = get_random_tangent_point_between_point_n_sphere(sphere_center, sphere_radius, given_point)
    circle_center, dir_vector = get_3dline_equation(circle_center, random_tangent_point)
    
    random_ratio = np.random.uniform(low = 0, high=ratio_high)
    random_point = circle_center + dir_vector * random_ratio
    return random_point

def get_random_point_on_3dplane(cartersian_coeffs, low = -2, high = 2):
    '''
    cartesian_coeffs: tuple of a, b, c, d where ax + by + cz + d = 0
    '''
    a,b,c,d = cartersian_coeffs
    x, y = np.random.uniform(low=low, high=high, size= (1,))[0], np.random.uniform(low=low, high=high, size= (1,))[0]
    z = (-d -a*x-b*y)/ (c + 1e-5)
    return x, y, z

def get_random_point_on_3dline(pointA, pointB):
    '''
    Return random points on a 3d linestring, given the boundary of the line
    output: 3d point as np.array
    '''
    x0_y0_z0, dir_vector = get_3dline_equation(pointA, pointB)
    return x0_y0_z0 + random.uniform(0,1) * dir_vector

def get_sphere_equation(center, radius):
    '''
    vector form equation of a sphere, given center and radius: (point-center)^2 = radius^2 = point^2 -2*point*center + center^2
    output: -2*center, center^2 - radius^2
    '''
    assert len(center) == 3, f"Invalid center for sphere with length {len(center)}"
    return -2* center, np.square(center) - np.square(radius)

def get_random_point_on_circle_xyplane(center, radius):
    '''
    Return random point on a 2d circle on the xy plane
    input: 
    - center: (x0, y0)
    - radius: r
    then (x - x0)^2 + (y - y0)^2 = r^2
    output: 2d point as np.array
    
    '''
    x0, y0, z0= center

    x_squareterm = random.uniform(0, radius**2)
    x = sqrt(x_squareterm) * (2*(0.5 -bool(random.getrandbits(1)))) + x0  #randomly get the positive or negative of the sqrt term
    y = sqrt(radius**2 - x_squareterm) * (2*(0.5 -bool(random.getrandbits(1)))) + y0
    return (x, y)

def get_random_point_on_sphere(center, radius):
    '''
    Return random point on a 3d sphere
    input: 
    - center: (x0, y0, z0)
    - radius: r
    then (x - x0)^2 + (y - y0)^2 + (z - z0)^2 = r^2
    output: 3d point as np.array
    '''
    x0, y0, z0= center
    x_squareterm = random.uniform(0, radius**2)
    x = sqrt(x_squareterm) * (2*(0.5 -bool(random.getrandbits(1)))) + x0  #randomly get the positive or negative of the sqrt term
    
    y_squareterm = random.uniform(0, radius**2 - x_squareterm)
    y = sqrt(y_squareterm) * (2*(0.5 -bool(random.getrandbits(1)))) + y0  #randomly get the positive or negative of the sqrt term

    z = sqrt(radius**2 - x_squareterm - y_squareterm)  * (2*(0.5 -bool(random.getrandbits(1)))) + z0
    return (x, y, z)

def plot_3d(point, line):
    fig = plt.figure(figsize=(4,4))
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(point[0], point[1], point[2], c='r') # plot the point (2,3,4) on the figure

    for p in line:
        ax.scatter(p[0], p[1], p[2],c = 'b')
    plt.show()

def main():
    # furthest_surface_points = get_random_point_on_3dpolygon(num_points= 4,max_abs_x= 36,max_abs_y= 20, z_coord= 100)
    # closest_surface_points = get_random_point_on_3dpolygon(num_points= 4, max_abs_x= 3.5,max_abs_y= 1, z_coord= 8)
    # points = []
    # for point_pair in zip(furthest_surface_points, closest_surface_points):
    #     points.append(
    #         get_random_point_on_3dline(point_pair[0], point_pair[1])
    #     )
    # print(points)

    #Test viz
    # line = []
    # for i in range(50):
    #     line.append(get_random_point_on_3dline(np.array([36, 20, 100]), np.array([3.5, 1, 8])))
    # point = get_random_point_on_3dline(np.array([36, 20, 100]), np.array([3.5, 1, 8]))
    # plot_3d(point = point, line = line)

    center = (0,0,0)
    given_point = (7,9,12)
    radius = 12
    
    get_random_tangent_point_between_point_n_sphere(center=center, radius=radius, given_point=given_point)

if __name__ == "__main__":
    main()

