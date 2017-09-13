import numpy as np
import math
import matplotlib.pyplot as plt

class MapPlotter:
    """A class that will plot a map in Plate Carree projection.
    Internally the map is represented as a 1D Array to ease matrix operations
    """
    
    def __init__(self, boxSize):
        """Generate the map grid points
         Parameter: boxSize: Map grid in km (at equator)"""

        radiusOfEarth = 6371e3;
        self.sizeLon = round(2*math.pi*radiusOfEarth / boxSize);
        self.xLim = 180;
        self.offsetLon = self.sizeLon / 2;
        self.scaleLon = np.linspace(-self.xLim, self.xLim, self.sizeLon);
        self.sizeLat = round(2*math.pi*radiusOfEarth / boxSize / 2);
        self.yLim = 90;
        self.offsetLat = self.sizeLat / 2;
        self.scaleLat = np.linspace(-self.yLim, self.yLim, self.sizeLat);
        
        self.accum = np.zeros(self.sizeLon * self.sizeLat);
        self.count = np.zeros(self.sizeLon * self.sizeLat);
        
    def accumulateDataToMap(self, longitudeArray, latitudeArray, vals):
        """ Function that adds data to map accumulation and count of data
        so that average can be calculated.
        Inputs: 1D Numpy array of each of latitude, longitude and values
        """
        #longitudeArray = np.zeros(1);
        #latitudeArray =  np.zeros(1);
        #vals = np.ones(1);
        xScaled = np.round(longitudeArray / self.xLim * self.sizeLon/2 + self.offsetLon);
        yScaled = np.round(latitudeArray / self.yLim * self.sizeLat/2 + self.offsetLat);
        #print(self.sizeLon)
        #print(self.sizeLat)
        #print(xScaled)
        #print(np.shape(self.accum))
        linearisedLocation = (xScaled-1) + self.sizeLon * (yScaled-1);
        #Saturate the rounding
        #linearisedLocation[linearisedLocation > np.shape(self.accum)[0]] = np.shape(self.accum)[0];
        
        #Average across duplicates
        uniqueLocations = np.unique(linearisedLocation);
        for i in range(0, np.shape(uniqueLocations)[0]-1):
            location = uniqueLocations[i].astype(int);
            #Increase the accum and count ignoring data that are NaNs
            addCount = np.sum(np.isfinite(vals[linearisedLocation == location]));
            addValue = np.nansum(vals[linearisedLocation == location]);
            
            self.accum[location] = self.accum[location] + addValue;
            self.count[location] = self.count[location] + addCount;

    def plotMap(self):
        '''Plot the map'''
        
        accum2D = np.reshape(self.accum, (self.sizeLat, self.sizeLon))
        count2D = np.reshape(self.count, (self.sizeLat, self.sizeLon))

        mapAverage = np.divide(accum2D, count2D)
        
        mapAverage = np.flipud(mapAverage)
        
        # Mask array to only where there is data
        #mapAverage = np.ma.masked_where(count2D < 0, mapAverage)
        
        #mapAverage = np.random.random((200,100))
        
        plt.figure(figsize=(10,10))
        plt.imshow(mapAverage, cmap='jet', interpolation='none', extent=[-self.xLim, self.xLim, -self.yLim, self.yLim])
                
        plt.xticks(np.arange(-180,181,45), fontsize=10)
        plt.yticks(np.arange(-90,91,45), fontsize=10)
        
        plt.tight_layout()
        plt.show()
        
    def plotMapStatic(self, map):
        '''Plot the map'''
        
        map = np.flipud(map)
        
        plt.figure(figsize=(10,10))
        plt.imshow(map, cmap='jet', interpolation='none', extent=[-self.xLim, self.xLim, -self.yLim, self.yLim])

        plt.xticks(np.arange(-180,181,45), fontsize=10)
        plt.yticks(np.arange(-90,91,45), fontsize=10)
        
        plt.tight_layout()
        plt.show()
        