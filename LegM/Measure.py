#!/usr/bin/python3
from LegM.legAnalysisclassThread import LegAnalysisClass
from LegM.roi import Roi
from LegM.temperaturemonitor import TemperatureMonitor


import picamera
import time
#from LT.controlLED import ControlLED 
import numpy as np

def medir(basePath):
#     basePath = '/home/pi/Desktop/WALKING/'
    print("\n-----DELETE or move to another folder all the files in Desktop/flyWALKING")
    file = input("\nEnter a name for the output file or press Enter for default name (YearMonthDay_HH-MM): ")
    fecha = time.strftime("%Y%m%d_%H-%M",time.gmtime())
    if len(file) == 0:
        nameOfFile = fecha
        print(f"default name is: {fecha}" )
    else:
        nameOfFile = file 
    
    try:
        monitor = TemperatureMonitor(30)
    
    except ModuleNotFoundError as error:
        print(f"error {error}")
        
    with picamera.PiCamera() as camera:
        camera.resolution = (1344,752)
        camera.framerate = 10 #do not delete. it allows for fast camera warm up. if set to 1, movement is detected while camera warms up
        camera.vflip = True
        camera.hflip = True
        camera.led = False
        camera.exposure_mode = "auto"
        camera.brightness = 50
        time.sleep(1)
        camera.framerate = 1
       # camera.awb_mode = "off"
        #camera.awb_gains = (1.3,1.6) #red,blue
        areas = Roi()
        output = LegAnalysisClass(camera, nameOfFile,basePath,areas,monitor)
        video = 1
        camera.start_recording(output, splitter_port=2, format='bgr')
        
        time1=time.time()
        print(f"basePath: {basePath}")
        for filename in camera.record_sequence(( 
            (basePath + "/"+ nameOfFile +"--%05d.h264") % i for i in range(1,289)), bitrate = 1000000 ):
            camera.wait_recording(300)
            print("video" + str(video))
            video += 1
        camera.stop_recording(splitter_port=2)
      
        #x=ControlLED()
        #x.GPIO_clean()

    #   camera.start_recording(output, splitter_port=2, format='bgr')
        
    camera.close()
    monitor.stop()
    #         camera.stop_recording()
    # fin = np.full((38,50,3),200,dtype=np.uint8)
    # output.analyse(fin)      


    t = time.time()-time1
    if t < 60:
        print("tiempo total: " + str(t) + " seg.")
    elif t >= 60 and t < 3600:
        print("tiempo total: " + str(t/60) + " min")
    elif t >= 3600:
        print("tiempo total: " + str(t//3600) + " hr " + str((t%3600//60)) + " min")      
    
    
#     outputFile = nameOfFile + ".csv"
#     return outputFile
    return nameOfFile

if __name__ == "__main__":
    medir()
