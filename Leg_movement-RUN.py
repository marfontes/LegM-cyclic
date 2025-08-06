#!/usr/bin/env python3
from LegM.Measure import medir
from LegM.graphEventPi import makeGraph
import os
#import LT.convert as convert
import sys
#from LT.setupWF import setup
import logging

logging.basicConfig(level=logging.DEBUG)

basePath = os.path.join(os.path.expanduser("~/Desktop"),"LegFiles")
if not os.path.exists(basePath):
    os.mkdir(basePath)
os.chown(basePath, 1000, 1000)

#setup()
outputFile = medir(basePath)
makeGraph(basePath, outputFile)
#convert.mp4(basePath, outputFile)

sys.exit()
