#!/usr/bin/env python3
# from LT.analysisclass import AnalysisClass
from LegM.roi import Roi
import picamera
import picamera.array
# import argparse
import cv2
import os
import json


def setup():
    basePath = os.path.join(os.path.expanduser("~/Desktop"),"LegFiles")
    
    if not os.path.exists(basePath):
            #os.chdir('/home/pi/Desktop/')
        os.mkdir(basePath)
        os.chown(basePath, 1000, 1000)
        
    camera = picamera.PiCamera()
    camera.resolution = (1344,752)
    camera.vflip = True
    camera.hflip = True
    camera.framerate = 10
    rawCapture = picamera.array.PiRGBArray(camera, size=(1344,752))
    camera.exposure_mode = "auto"
#     camera.awb_mode = "auto"
    camera.brightness = 50
#     time.sleep(1)
    #camera.awb_mode = "off"
    #time.sleep(3)
    #print(camera.awb_gains)
    #camera.awb_gains = (1.3, 1.6) #red,blue

    areas = Roi()
        
    nameW = "press Enter to select ROIs"
    for cuadro in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        frame= cuadro.array
        cv2.imshow(nameW,frame)
        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)
        if key == 13:
            cv2.destroyAllWindows()
            break
    
    camera.close()
    nameW="select ROIs. Press 'c' to CLOSE"
    if areas.start:
        cv2.namedWindow(nameW)
        cv2.setMouseCallback(nameW,areas.click)
        image = frame.copy()
        cropped = areas.crop(image)
        print(f"cropped size {cropped.shape}")
    
    while areas.start: 
        if areas.change == True:
            cropped = areas.setRois(cropped)
        cv2.imshow(nameW,cropped)        
        key = cv2.waitKey(100) & 0xFF
        if key == ord("c"):
            if len(areas.listROIs) == 0:  #evalua si se cargaron ROIs /// 
                continue
            
             # Convert the list of arrays to a list of lists
            roi_list = [arr.tolist() for arr in areas.listROIs]
            roi_list.append(areas.rectangle)
            
            
            ##### AGREGAR A LA LISTA LOS PUNTOS PARA HACER EL CROP
            ## VER SI SE PUEDEN PONER PUNTOS DE REFERENCIA POR S LA PUPA SE MUEVE, REORIENTAR LOS ROIs
            
            
             # Save the list of lists as a JSON file
            with open("roi_list.json", "w") as f:
                json.dump(roi_list, f)
            cv2.imwrite(os.path.join(basePath,"roi.png"),cropped)
            areas.list_masks(areas.rectangle[2], areas.rectangle[3])   #x,y,w,hcrea una lista de máscaras para cada roi
            for mask in areas.listMasks:
                cv2.imshow("mask",mask)
                cv2.waitKey(200)                    
            areas.start = False
            cv2.destroyWindow(nameW)
            cv2.destroyWindow("mask")

            

#             key = cv2.waitKey(1) & 0xFF
#                 # if the 'q' key is pressed, stop the loop
#             if key == ord("q"):
#                 break
#             elif key == 13:
#                 break
#             ##        cv2.destroyAllWindows()
#                 
#         cv2.imshow("trr",frame)        
#         cv2.waitKey(1) & 0xFF
        
#     camera.release()
        
    camera.close()
    
if __name__ == "__main__":
    setup()


      
