'''
main() modified from https://github.com/amusi/Non-Maximum-Suppression/blob/master/nms.py
For generation, nms will be ignorant of confidence score, and will only concern area of overlap (iou)
'''
import cv2
import numpy as np

"""
    Non-max Suppression Algorithm

    @param list  Object candidate bounding boxes
    @param list  Confidence score of bounding boxes
    @param float IoU threshold

    @return Rest boxes after nms operation
"""

def iou(bbox1, bbox2):
    '''
    modified from 
    https://learnopencv.com/non-maximum-suppression-theory-and-implementation-in-pytorch/
    '''
    ((x1, y1), (a1, b1)) = bbox1
    ((x2, y2), (a2, b2)) = bbox2

    # find the area for the box1 (x1,y1) (a1,b1)
    area1 = (a1-x1)*(b1-y1)
    
    # find the area for the box2 (x2,y2) (a2,b2)
    area2 = (a2-x2)*(b2-y2)
    
    # Now we need to find the intersection box
    # to do that, find the largest (x, y) coordinates 
    # for the start of the intersection bounding box and 
    # the smallest (x, y) coordinates for the 
    # end of the intersection bounding box
    xx = max(x1, x2)
    yy = max(y1, y2)
    aa = min(a1, a2)
    bb = min(b1, b2)
    
    # So the intersection BBox has the coordinates (xx,yy) (aa,bb)
    # compute the width and height of the intersection bounding box
    w = max(0, aa - xx)
    h = max(0, bb - yy)
    
    # find the intersection area
    intersection_area = w*h
    
    # find the union area of both the boxes
    union_area = area1 + area2 - intersection_area
    
    # compute the ratio of overlap between the computed
    # bounding box and the bounding box in the area list
    IoU = intersection_area / union_area

    return area1, area2, intersection_area, union_area, IoU

def bbox_coord_extract(bbox):
    # coordinates of bounding boxes
    upper_left_x = bbox[0][0]
    upper_left_y = bbox[0][1]
    lower_right_x = bbox[1][0]
    lower_right_y = bbox[1][1]
    return upper_left_x, upper_left_y, lower_right_x, lower_right_y

def nms(bboxes, overlap_thres = 0.75):
    '''
    Iterate over each box, compare area and overlap ratio. If the smaller box is occluded by the bigger box (overlap_ratio > overlap_threshold),
    remove the box that is being iterated on
    input:
    bboxes: list of tuple of 2 tuples, each is a coordinate of upper_left and lower_right
    overlap_threshold
    '''
    # If no bounding boxes, return empty list
    if len(bboxes) == 0:
        return [], []
    
    picked_indices = []
    picked_bboxes = []
    
    for i in range(len(bboxes)):
        cur_bbox = [0,0]
        areas = [0,0]
        cur_bbox[0] = bboxes[i] 
        if bboxes[i+1:] == []:
            picked_indices.append(i)
            picked_bboxes.append(bboxes[i])
            break

        for j in range(len(bboxes[i+1:])):
            
            cur_bbox[1] = bboxes[i+1:][j]
            areas[0], areas[1], intersection_area, union_area, IoU = iou(cur_bbox[0], cur_bbox[1])
            
            smaller_box_index = 0 if areas[0] < areas[1] else 1 #The box larger
            #For the smaller box
            smaller_overlap_ratio = intersection_area/areas[smaller_box_index]
                        
            if smaller_overlap_ratio > overlap_thres:
                print(smaller_overlap_ratio, 'break')
                break
        else: 
            picked_indices.append(i)
            picked_bboxes.append(bboxes[i])

    return picked_bboxes, picked_indices

if __name__ == '__main__':
    # Image name
    image_name = 'basic_function_testing/test_basic_func.png0001.png'

    # Bounding boxes
    bounding_boxes = [((187, 82), (337, 317)), ((150, 67), (305, 282)), ((246, 121), (368, 304))]
    # confidence_score = [0.9, 0.75, 0.8]

    # Read image
    image = cv2.imread(image_name)

    # Copy image as original
    org = image.copy()

    # Draw parameters
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    thickness = 2

    # IoU threshold
    threshold = 0.4

    # Draw bounding boxes and confidence score
    for index, ((start_x, start_y), (end_x, end_y)) in enumerate(bounding_boxes):
        (w, h), baseline = cv2.getTextSize(str(index), font, font_scale, thickness)
        cv2.rectangle(org, (start_x, start_y - (2 * baseline + 5)), (start_x + w, start_y), (0, 255, 255), -1)
        cv2.rectangle(org, (start_x, start_y), (end_x, end_y), (0, 255, 255), 2)
        cv2.putText(org, str(index), (start_x, start_y), font, font_scale, (0, 0, 0), thickness)

    # Run non-max suppression algorithm
    picked_boxes, picked_indices = nms(bounding_boxes, threshold)

    # Draw bounding boxes and confidence score after non-maximum supression
    for index, ((start_x, start_y), (end_x, end_y))  in enumerate(picked_boxes):
        (w, h), baseline = cv2.getTextSize(str(picked_indices[index]), font, font_scale, thickness)
        cv2.rectangle(image, (start_x, start_y - (2 * baseline + 5)), (start_x + w, start_y), (0, 255, 255), -1)
        cv2.rectangle(image, (start_x, start_y), (end_x, end_y), (0, 255, 255), 2)
        cv2.putText(image, str(picked_indices[index]), (start_x, start_y), font, font_scale, (0, 0, 0), thickness)

    # Show image
    cv2.imshow('Original', org)
    cv2.imshow('NMS', image)
    cv2.waitKey(0)