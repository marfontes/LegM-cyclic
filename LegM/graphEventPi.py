#! /usr/bin/env python3
#import numpy as np
import pandas as pd
#import matplotlib
#matplotlib.use("Agg")
import matplotlib.pyplot as plt
#import matplotlib.patches as mpatches
#import matplotlib.ticker as ticker
import os
#import time
#import csv
#from pathlib import Path
from LegM.stimuli import TempRange

def makeGraph(basePath, outputFile):
    data = outputFile +".csv"
    for filename in os.listdir(basePath):
        if filename.endswith(".csv"):
            
#        if filename == data:
            print(f"\n-----Analyzing data in {filename} -----")
            #print(f"\n-----Analyzing data in {data} -----")
##            time.sleep(1)
            newname = filename.split(".csv")[0]
          #  file= basePath +"/"+ data
#            destDF = pd.read_csv(basePath +"/"+ data, sep=",")
            destDF = pd.read_csv(basePath +"/"+ filename, sep=",")
            print("indicate which of the following ROIs you want to graph, separated by comma, and press Enter")
            a=list(destDF.columns[3:])
            for i in range(len(a)):
                print(a[i])
            print( "Example: 1,3  <ENTER>")
            print( "or just press Enter to graph all ROIs")
            text = input()
            headers = text.split(",")
            for i in range(len(headers)):
                if headers[i]== "":
                    print("all ROIs will be used")
                    headers = []
                    numberROIs = len(destDF.axes[1])-3
                    for i in range(numberROIs):
                        headers.append(destDF.columns[i+3])
                    newname = newname + "-allROIs"
                else:
                    headers[i] = "ROI " + headers[i]
                    newname = newname + "-" + headers[i]
            newname2 = basePath +"/" + newname + ".png"
            numberROIs = len(headers)
            print("making graph")

            numberofgraphs = round((len(destDF)/3600)+0.5)
            alto = numberofgraphs*2.5
            plt.figure(figsize=(9,alto))
            maxList= []
            for i in range(len(headers)):
                maxValue = destDF.loc[:,headers[i]].max()
                maxList.append(maxValue)
##            print(maxList)
            maxValue = max(maxList)
##            print(maxValue)


            #colors = ['r','b', 'g', 'y', 'c', 'm', 'k', 'w','b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
            colors = [f'C{i}' for i in range(numberROIs)]

            
            for j in range(numberofgraphs):
                inicio = 3600*j
                fin = 3599 + 3600*j
                plt.subplot(numberofgraphs,1,j+1)
                plt.title(("hour " + str(j+1)), loc="right")#, pad="-15")
                tempData = destDF.loc[inicio:fin, "temp"]         
                boundaries = TempRange()
                limitsLow, limitsHigh = boundaries.set_ranges(tempData,fin)

                for x,y in limitsLow:
                    plt.axvspan(x,y,0.05,0.95,color="whitesmoke") 
                for x,y in limitsHigh:
                    plt.axvspan(x,y,0.05,0.95,color="papayawhip")                
                
                event = True
#################### USANDO DATOS ORIGINALES
##                for i in range(len(headers)):
##                    plt.plot(destDF.loc[inicio:fin,"time"], destDF.loc[inicio:fin,headers[i]]+maxValue*i, color=colors[i],linewidth=1)#,markersize=5)#,mfc=black
##                plt.ylim(top= maxValue*(len(headers)+1))#, bottom = -5)
##                offset = maxValue
##                event = False
                
#######  FILTRANDO filtrando al 1% (baja a cero) y si es mayor queda como 5
##                for i in range(len(headers)):
##                    y_values = destDF.loc[inicio:fin, headers[i]]  # Extract y-values
##                    y_values = np.where(y_values <= 1, 0, 5)  # Convert values < 1 to 0
##                    y_values = y_values + 6 * i    
##                    plt.plot(destDF.loc[inicio:fin,"time"], y_values, color=colors[i],linewidth=1)#,markersize=5)#,mfc=black
##                plt.ylim(top= 8*(len(headers)))#, bottom = -5)
##                plt.tick_params(axis="y", left= False,labelleft =False)              
##                event = False

#######  EVENT PLOT: filtrando al 1% (baja a cero). EN LOS QUE PASAN EL UMBRAL, EL DATO DE TIEMPO PASA A SER EL DATO DEL EJE Y: CUÁNDO OCURRIÓ EL EVENTO
                if event:
                    data1 = []
                    filter_value = 0.5
                    for i in range(len(headers)):
                        y_values = destDF.loc[inicio:fin, headers[i]]  # Extract y-values
                        filtered_indices = y_values[y_values > filter_value].index
                        data1.append(filtered_indices)
                    offset = 4
                    plt.eventplot(data1, colors=colors, linelengths=3, lineoffsets=offset, linewidths = 1)
                    plt.suptitle(f'filter {filter_value} %', fontsize=16)
                    #positions = []
                    #for i in range(len(headers)):
                    #    positions. append(i * offset)
                    #plt.yticks(positions, headers)  # Set the positions where the labels will appear

                positions = []   ##calcula donde poner las etiquetas del ejeY 
                for i in range(len(headers)):
                    positions. append(i * offset)
                plt.yticks(positions, headers)
                    
                left_limit = destDF.loc[inicio,"time"]
                right_limit = left_limit + 3600

                labels = [0,10,20,30,40,50]
                ticks =[]
                for i in range(6):
                    ticks.append(left_limit+ (600*i))
                plt.xticks(ticks,labels)

                plt.xlim(left= left_limit, right=right_limit)
                #plt.legend(headers, loc = "upper left", ncol = len(headers))
                
                if j<numberofgraphs-1:
                    plt.tick_params(axis="x", labelbottom =False)

            
            plt.tight_layout() 
            plt.savefig(newname2)
##            plt.show()
           

if __name__ == "__main__":
    #basePath = str(Path().absolute())
    basePath = "/home/locomotionlab/Desktop/LegFiles"
    outputFile =  "intensityValues"
    makeGraph(basePath,outputFile)

