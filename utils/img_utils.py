
import cv2
import random
import numpy as np

UV_DEFAULT_SHAPE = (1024,1024,3)
SINGLE_SIDE_LEN = int(UV_DEFAULT_SHAPE[0]//8)

def img_random_rotate_by_90(matrix):
    if bool(random.getrandbits(1)):
        return np.rot90(matrix) 
    return matrix 

def stitching_upwrapped_texture(single_side_texture_path, obj_type, output_path):

    single_side = cv2.imread(single_side_texture_path)
    uv_arr  = np.random.normal(0,255,UV_DEFAULT_SHAPE)
    
    #Cut a square out of the original single side image, if it's not already a square
    if single_side.shape[0] != single_side.shape[1]:
        min_size = min(single_side.shape[0], single_side.shape[1])    
        single_side = single_side[0: min_size+1, 0: min_size+1, :]

    if obj_type == '1u':
        ratio = 2
        indices = [(0,2,3,5), (2,4,3,5), (4,6,3,5), (6,8,3,5), (2,4,1,3), (2,4,5,7)]
    elif obj_type == '2u':
        ratio = 1
        indices = [
            (0,1,1,2),
            (1,2,1,2),
            (2,3,1,2),
            (3,4,1,2),(3,4,0,1),(3,4,2,3),
            (4,5,1,2),(4,5,0,1),(4,5,2,3),
            (5,6,1,2),
        ]
    elif obj_type == '3u':
        ratio = 1
        indices = [(3.5, 4.5, 0, 1), (3.5,4.5,1,2), (3.5,4.5,2,3), (3.5,4.5,3,4), (3.5,4.5,4,5), (3.5,4.5,5,6), (3.5,4.5,6,7),\
                (3.5,4.5,7,8), (2.5,3.5,1,2), (2.5,3.5,2,3), (2.5,3.5,3,4), (4.5,5.5,1,2), (4.5,5.5,2,3), (4.5,5.5,3,4)]
    elif obj_type == '4u':
        ratio = 1
        indices = [
            (0,1,1,2), (0,1,2,3),
            (1,2,1,2), (1,2,2,3), 
            (2,3,1,2), (2,3,2,3),
            (3,4,1,2),(3,4,0,1),(3,4,2,3),(3,4,3,4),
            (4,5,1,2),(4,5,0,1),(4,5,2,3),(4,5,3,4),
            (5,6,1,2),(5,6,2,3),
        ]
    elif obj_type == '6u':
        ratio = 1
        indices = [(3, 4, 0, 1), (3,4,1,2), (3,4,2,3), (3,4,3,4), (3,4,4,5), (3,4,5,6), (3,4,6,7),(3,4,7,8),\
            (4, 5, 0, 1), (4, 5,1,2), (4, 5,2,3), (4, 5,3,4), (4, 5,4,5), (4, 5,5,6), (4, 5,6,7),(4,5,7,8),\
            (2, 3,1,2), (2, 3,2,3), (2, 3,3,4),
            (5, 6,1,2), (5, 6,2,3), (5, 6,3,4),
        ]
    elif obj_type == '12u':
        ratio = 0.5
        indices = [
            (0, 0.5, 1,1.5),(0,0.5, 1.5,2),
            (0.5, 1, 1,1.5),(0.5,1, 1.5,2),
            (1, 1.5, 1,1.5),(1,1.5, 1.5,2),
            (1.5, 2, 1,1.5),(1.5,2, 1.5,2),
            (2, 2.5, 1,1.5),(2,2.5, 1.5,2),
            (2.5, 3, 1,1.5),(2.5,3, 1.5,2), (2.5, 3, 0,0.5),(2.5,3, 0.5,1), (2.5, 3, 2,2.5),(2.5,3, 2.5,3), 
            (3, 3.5, 1,1.5),(3,3.5, 1.5,2), (3, 3.5, 0,0.5),(3,3.5, 0.5,1), (3, 3.5, 2,2.5),(3,3.5, 2.5,3),
            (3.5, 4, 1,1.5),(3.5,4, 1.5,2), (3.5, 4, 0,0.5),(3.5,4, 0.5,1), (3.5, 4, 2,2.5),(3.5,4, 2.5,3),
            (4, 4.5, 1,1.5),(4,4.5, 1.5,2),
            (4.5, 5, 1,1.5),(4.5,5, 1.5,2),
        ]
    
    single_side = cv2.resize(single_side, dsize=(int(SINGLE_SIDE_LEN*ratio), int(SINGLE_SIDE_LEN*ratio)), interpolation=cv2.INTER_AREA)
    for index in indices:
        uv_arr[int(SINGLE_SIDE_LEN*index[0]): int(SINGLE_SIDE_LEN*index[1]),int(SINGLE_SIDE_LEN*index[2]):int(SINGLE_SIDE_LEN*index[3]), :] = img_random_rotate_by_90(single_side)

    cv2.imwrite(img = uv_arr, filename=output_path)

def main():
    obj_type = '4u'
    stitching_upwrapped_texture(
        single_side_texture_path='/home/anhnguyen/Documents/SpaceTargetRenderer/asset/space_targets/cubesats/textures/one_side/solar/uvlayout1.png',
        obj_type = obj_type,
        output_path = f'/home/anhnguyen/Documents/SpaceTargetRenderer/asset/space_targets/cubesats/textures/uvlayout1_{obj_type}.png'
    )

if __name__ == '__main__':
    main()