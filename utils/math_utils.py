import random
import numpy as np
import matplotlib.pyplot as plt

from math import radians

def get_random_rotation_offset():
    return radians(random.uniform(0, 180))

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
    #direction vector t
    dir_vector = pointB - pointA
    #r(t) = pointA + t*dir_vector
    # print('Equation')
    # print(pointA, pointB, dir_vector ) #TODO delete
    return pointA, dir_vector

def get_random_point_on_3dline(pointA, pointB):
    '''
    Return random points on a 3d linestring, given the boundary of the line
    output: 3d point as np.array
    '''
    x0_y0_z0, dir_vector = get_3dline_equation(pointA, pointB)
    return x0_y0_z0 + random.uniform(0,1) * dir_vector

def plot_3d(point, line):
    fig = plt.figure(figsize=(4,4))
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(point[0], point[1], point[2], c='r') # plot the point (2,3,4) on the figure

    for p in line:
        ax.scatter(p[0], p[1], p[2],c = 'b')
    plt.show()


def main():
    furthest_surface_points = get_random_point_on_3dpolygon(num_points= 4,max_abs_x= 36,max_abs_y= 20, z_coord= 100)
    closest_surface_points = get_random_point_on_3dpolygon(num_points= 4, max_abs_x= 3.5,max_abs_y= 1, z_coord= 8)
    points = []
    for point_pair in zip(furthest_surface_points, closest_surface_points):
        points.append(
            get_random_point_on_3dline(point_pair[0], point_pair[1])
        )
    print(points)

    #Test viz
    # line = []
    # for i in range(50):
    #     line.append(get_random_point_on_3dline(np.array([36, 20, 100]), np.array([3.5, 1, 8])))
    # point = get_random_point_on_3dline(np.array([36, 20, 100]), np.array([3.5, 1, 8]))
    # plot_3d(point = point, line = line)

if __name__ == "__main__":
    main()

