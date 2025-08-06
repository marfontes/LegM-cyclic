#!/usr/bin/env python3
# import the necessary packages
import threading
import time
from w1thermsensor import W1ThermSensor
from w1thermsensor.errors import NoSensorFoundError
import RPi.GPIO as GPIO

###en este, la ID es dada por well y no por next object ID

class TemperatureMonitor():
    def __init__(self, setPoint=None, hysteresis=0.8):
        try:
            self.sensor = W1ThermSensor()
            self.temperature = None
            self.sensorFound = True
            self.running = True
            self.thread = threading.Thread(target=self._update_temperature)
            self.thread.start()
            
            
            GPIO.setwarnings(False)
            GPIO.cleanup()
            GPIO.setmode(GPIO.BCM)
            self.relayPin = 5 #17 #physical pin 11
            GPIO.setup(self.relayPin, GPIO.OUT, initial = GPIO.LOW) # We have set our LED pin mode to output
            self.setPoint = setPoint
            self.hysteresis = hysteresis
            self.heating = True
            self.SP_changed = True
            self.high_window = 60*10 #20 minutos, time window starts when high temp is reached
            self.window_start = None
            self.low_window = 60 * 20  #now the script will start the low window as soon as the setpoint is changed from high to low, not when the low temp is reached
            self.mode = "heat"
            self.start = time.time()
            self.cycling_start = False
            
        except NoSensorFoundError: #as error:
            print("no encontró sensor")
            self.temperature = "RoomTemp"
            self.sensorFound = False
        
    
    def _update_temperature(self):
        if self.sensorFound :
            while self.running:
                self.temperature = self.sensor.get_temperature()
                self.control_relay()
                time.sleep(1)     
        else:
            pass
    
    def stop(self):
        if self.sensorFound :
            self.running = False
            self.thread.join()
            GPIO.cleanup()
        else:
            pass
    
    def control_relay(self):
        if self.setPoint != None and time.time() - self.start > 60: #1800: #no entra acá hasta que no haya pasado media hora
            
            if self.heating:
                if self.temperature < self.setPoint:
                    GPIO.output(self.relayPin, GPIO.HIGH)
                else:
                    GPIO.output(self.relayPin, GPIO.LOW)
                    if self.cycling_start == False:
                        self.cycling_start = True
                        self.window_start = time.time()
                    if self.SP_changed:
                        self.window_start = time.time()
                        self.SP_changed = False
                    self.heating = False
            else:
                if self.temperature <= self.setPoint-self.hysteresis:
                    self.heating = True
            self.temp_cycling()
    
    def temp_cycling(self):
        if self.cycling_start:
            if self.mode == "heat":
                if time.time()- self.window_start > self.high_window:
                    self.change_setPoint(26)
                    print( time.time()- self.window_start )
            if self.mode == "cool":
                if time.time()- self.window_start > self.low_window:
                    self.change_setPoint(30)
    
    def change_setPoint(self,value):
        if value-self.setPoint > 0:
            self.mode = "heat"
        elif value-self.setPoint < 0:
            self.mode = "cool"
        self.setPoint = value
        self.heating = True
        self.SP_changed = True
        