import cv2
import numpy as np
##from random import randint
import os
import time
import pandas as pd
##from collections import OrderedDict
import csv
import json


class Roi():
    def __init__(self):
        self.listROIs = []
        self.listVertices = []
        self.finish = False
        self.ROInumber = 0
        self.change = False
        self.listMasks = []
        self.listMasksPixels = []
        self.lastFrame = None
        self.rectangle = (0,0,0,0)
        self.start = True
        self.intensityValues = []
        self.ROIoverlay = None
        self.columnNames = None
        

    def click(self,event,x,y,flags,param):
        #global listROIs, finish, listVertices, ROInumber
        
        if event ==cv2.EVENT_LBUTTONDOWN:
            self.listVertices.append((x,y))
            self.change = True
#            cv2.circle(image, (x,y),1,(255,255,255),-1)


        if event == cv2.EVENT_RBUTTONDOWN:
            self.listVertices.append((x,y))
 #           cv2.putText(image, str(self.ROInumber),(x-15, y-10), cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,70,255),1)
  #          cv2.circle(image, (x,y),1,(255,255,255),-1)
            roi = np.array(self.listVertices, np.int32)
            roi = roi.reshape((-1,1,2))
   #         cv2.polylines(image,[roi],True,(0,255,255))
            self.listROIs.append(roi)
            self.listVertices = []
            self.ROInumber +=1
            self.change = True

    def list_masks(self,w,h):
        roiID = []
         
        for i,roi in enumerate(self.listROIs):
            black = np.zeros([h,w,1],dtype=np.uint8)
            black=cv2.drawContours(black,self.listROIs,i,(255),-1)
            self.listMasks.append(black)
            pixel_count = cv2.countNonZero(black)
            self.listMasksPixels.append(pixel_count)
            roiID.append("ROI " + str(i))
        self.columnNames = ["time", "temp"]+ roiID

    def crop(self,image):
        _, otsuT = cv2.threshold(image[:,:,2], 200, 255, cv2.THRESH_BINARY )#+ cv2.THRESH_OTSU)
        otsuT = cv2.dilate(otsuT, None, iterations=4)
        cnts = cv2.findContours(otsuT.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        #rrr = cv2.drawContours(image, cnts, -1, (0, 0, 255), 2)
        #cv2.imshow("ttre",rrr)
        #cv2.waitKey(0)
        if len(cnts) > 0:
            largest_contour = max(cnts, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            x = int(x-w/10)
            if x < 0:
                x = 0
            y = int(y-h/10)
            if y < 0:
                y = 0
            h = int(1.2*h)
            w = int(1.2*w)
            self.rectangle = x,y,w,h
            cropped = image[y:y+h,x:x+w,:]
        else:
            cropped = image
        return cropped
        
    def setRois(self,image):
        cropped = image
        for point in self.listVertices:
            cv2.circle(cropped, point,2,(0,0,0),-1)
            #cv2.circle(frame, point,2,(0,0,0),-1)
        for i,closed in enumerate(self.listROIs):
            cv2.polylines(cropped,[closed],True,(150,0,150),1)
            M = cv2.moments(closed)
            # Compute centroid coordinates
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])  # X coordinate
                cy = int(M["m01"] / M["m00"]) 
            cv2.putText(cropped, str(i),(cx,cy), cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,0),2) #(x-15, y-10)
        self.change = False
        return cropped
