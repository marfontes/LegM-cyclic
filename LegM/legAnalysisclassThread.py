#!/usr/bin/env python3

from LegM.graphEvent1h import Graph_1h
import picamera.array
import cv2
import time
import numpy as np
import pandas as pd
import os
from pathlib import Path
import csv
import sys
import threading
import json
from multiprocessing import Queue
import logging
import RPi.GPIO as GPIO

logging.basicConfig(level=logging.DEBUG)
logging.disable(logging.CRITICAL)

# ct = CentroidTracker()


class LegAnalysisClass(picamera.array.PiRGBAnalysis):
    def __init__(self,camera, nameOfFile,basePath,areas,monitor):
        super(LegAnalysisClass, self).__init__(camera)
        self.camera = camera
        self.areas = areas
        self.frames = 0
        self.totalFrames = 0
        self.start = 0
        self.a = 0
        self.selected_channel = 1
        self.contourThreshold = 0
        self.monitor = monitor
                
        current_script_path = os.path.abspath(__file__)
        # Directory containing the script
        script_dir = os.path.dirname(current_script_path)
        # One level above the script directory
        parent_dir = os.path.dirname(script_dir)
        
        
        filename = (parent_dir + "/roi_list.json")

        condition = os.path.exists(filename)
        if condition == False:
            print("\nRun setup first")
            input("\npress any key to quit")
            sys.exit()
            
        with open(filename,"r") as f:
            array_list_json = json.load(f)
                    # Convert the list of lists to a list of arrays
            self.areas.rectangle = array_list_json.pop(-1)# self.areas.listROIs.pop(-1)
            self.areas.listROIs = [np.array(arr) for arr in array_list_json]
            
        
        #make an image with the ROIs to overlay on the current image
        
        #x, y, w, h =areas.rectangle
        #crea una lista con las máscaras para cada ROI
        self.areas.list_masks(self.areas.rectangle[2], self.areas.rectangle[3]) 
        
        #crea una imagen con los ROis
        black1 = np.zeros([self.areas.rectangle[3],self.areas.rectangle[2],3],dtype=np.uint8) #x,y,w,h
#         for i,closed in enumerate(self.areas.listROIs):
#             cv2.polylines(black1,[closed],True,(100,100,0),2)
#             M = cv2.moments(closed)
#             # Compute centroid coordinates
#             if M["m00"] != 0:
#                 cx = int(M["m10"] / M["m00"])  # X coordinate
#                 cy = int(M["m01"] / M["m00"]) 
#             cv2.putText(black1, str(i),(cx,cy), cv2.FONT_HERSHEY_SIMPLEX,0.6,(100,100,0),2) #(x-15, y-10)
            
#         self.areas.ROIoverlay_template = black1
        self.areas.ROIoverlay = black1
        self.outfile = basePath + "/"+nameOfFile + ".csv"
        #self.settings = basePath + nameOfFile + ".png"
        
        self.graphQ = Queue(maxsize=1)
        self.live = Graph_1h(len(self.areas.listROIs),self.graphQ, self.monitor)
#         print(f"init: {self.default}  {self.outfile}")
            
    def nothing(self,j):
        pass
    
    def motionDetection(self, array, timestamp, totalFrames,temperature):
        #logging.debug("entra motion detection")
        #temperature = 25
        currentimage=[totalFrames, temperature] #ver si es conveneinte agregar timestamp
        #print("2")
        x, y, w, h = self.areas.rectangle
        cropped_channel = array[y:y+h,x:x+w,self.selected_channel]
        
        self.areas.ROIoverlay = array[y:y+h,x:x+w]
        for i,closed in enumerate(self.areas.listROIs):
            cv2.polylines(self.areas.ROIoverlay,[closed],True,(100,100,0),1)
            M = cv2.moments(closed)
            # Compute centroid coordinates
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])  # X coordinate
                cy = int(M["m01"] / M["m00"]) 
            cv2.putText(self.areas.ROIoverlay, str(i),(cx,cy), cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,0),2) #(x-15, y-10)

        if not self.monitor.sensorFound:
            t = temperature
            pos = (5,20)
        else:
            t = str(round(temperature,1))
            pos = (5,50)
            text = "setPoint " + str(self.monitor.setPoint)
            cv2.putText(self.areas.ROIoverlay, text,(5,20), cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,0),2) #(x-15, y-10)
            if GPIO.input(self.monitor.relayPin) == GPIO.HIGH:
                cv2.circle(self.areas.ROIoverlay,(70,42),10,(0,0,255),-1)
            elif GPIO.input(self.monitor.relayPin) == GPIO.LOW:
                cv2.circle(self.areas.ROIoverlay,(70,42),10,(0,0,0),1)
                
        cv2.putText(self.areas.ROIoverlay, t, pos, cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,0),2) #(x-15, y-10)       
        self.camera.annotate_text = t 
        #print(self.monitor.setPoint)
        #print(GPIO.input(self.monitor.relayPin))
        #self.areas.ROIoverlay = cv2.bitwise_or(array[y:y+h,x:x+w], self.areas.ROIoverlay_template)
        
        if self.areas.start:
            self.areas.lastFrame = cropped_channel
            self.areas.start = False
        
        subtract = cv2.subtract(cropped_channel,self.areas.lastFrame)
        _,th1 = cv2.threshold(subtract,10,255,cv2.THRESH_BINARY)
        cnts = cv2.findContours(th1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        filtered_contours = [cnt for cnt in cnts if cv2.contourArea(cnt) > self.contourThreshold]    #NOTE6: adjust minimum area
        black = np.zeros((h,w),dtype=np.int8)
        cv2.drawContours(black,filtered_contours,-1,255,-1)
        for i, mask in enumerate(self.areas.listMasks):
            #intensidad = cv2.mean(th1, mask=i)[0]
            intensidad = cv2.bitwise_and(black,black, mask=mask)
            #cv2.imshow("int",intensidad)
            intensidad = np.count_nonzero(intensidad)
            #intensidad = np.sum(intensidad)/255  #cuenta los puntos blancos dentro del ROI
            intensidad = intensidad*100/int(self.areas.listMasksPixels[i])
            currentimage.append(intensidad)
        #areas.intensityValues.append(currentimage)
        self.live.update(currentimage)
        #reshape currentimage as a list of lists, the data to be structured as a list of rows (each row should have 3 values, one for each column)
        currentimage = [currentimage]
        df = pd.DataFrame(currentimage, columns=self.areas.columnNames)
        #df = df.T
        
        if not os.path.isfile(self.outfile):
            df.to_csv(self.outfile)
        else:
            df.to_csv(self.outfile,mode="a", header=False)
       # logging.debug("termina motiion detection")
            # draw both the ID of the object and the centroid of the
            # object on the output frame
        
#         
        #cv2.imshow("Frame",array)
        self.areas.lastFrame = cropped_channel
        #cv2.imshow("Frame", self.areas.ROIoverlay)

        #cv2.waitKey(1)
        #print("analisis cuadro: " + str(time.time()-g))
    

    def analyse(self, array):
        self.frames += 1
#         print(self.frames)
#         cv2.namedWindow("Frame")
#         cv2.createTrackbar("Show values", "Frame", 1, 1, self.nothing)
        if self.frames % self.camera.framerate == 0:
            #print(time.time() - self.a)
            #print("tarda "+ str(time.time()-self.a))
            self.frames = 0
            self.totalFrames += 1
            
#             if self.totalFrames%10 == 0:
#                 self.monitor.change_setPoint(self.monitor.setPoint -1)
#             
            self.a = time.time() #no sé qué era esto
            timestamp = time.time()
            cv2.imshow("Frame", self.areas.ROIoverlay)
            cv2.waitKey(1)
            measureframe = threading.Thread(target = self.motionDetection,args=(array,timestamp, self.totalFrames, self.monitor.temperature))
            measureframe.start()
            
            ###########################################################3
            #######################################################3333333333333333333
            # acá hacer overlay de imagen completa con los ROIs, sirve para ver si se corrió la pupa
            # # Load your base image and contour image (must be same size)
#              overlay = cv2.bitwise_or(array, self.areas.ROIoverlay)
#            
#                 img = cv2.imread("base_image.jpg")
#                 contour_img = cv2.imread("contours.png")  # should be black except for contours
# 
#                 # Combine using bitwise_or
#                 overlay = cv2.bitwise_or(img, contour_img)
        if not self.graphQ.empty():
            logging.debug("reads queue")
            graph_bytes = self.graphQ.get()
            nparr = np.frombuffer(graph_bytes, np.uint8)
            graph = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            cv2.imshow("Graph",graph)
            cv2.waitKey(1)
            
        #cv2.waitKey(1) 
        
            
            
#         cv2.waitKey(1) & 0xFF
           
#             cv2.destroyAllWindows()
