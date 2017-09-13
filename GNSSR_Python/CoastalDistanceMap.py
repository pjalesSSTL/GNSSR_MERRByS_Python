import numpy as np
import h5py
import matplotlib.pyplot as plt
from GNSSR import *
from CoastalDistanceMap import *
from MapPlotter import *

class CoastalDistanceMap:
    """A class that can load a map of the distance to the nearest coast-line
    """
    
    def __init__(self):
        """Constructor"""

    def loadMap(self, filePath):
        """Load the distance to the coast map"""
        try:
            f = h5py.File(filePath, 'r')
        except OSError as e:
            #File does not exist
            #As TDS-1 is run periodically, many time segment files are not populated
            print("Could not find coastal distance map " + filePath)
            return

        self.coastalData = np.array(f['/array'])
        self.lats = np.array(f['/lats'])
        self.lons = np.array(f['/lons'])
        self.maxkm = np.array(f['/maxkm'])
        self.res = np.array(f['/res'])
        
        NaN = float('nan');
    
    def getDistanceToCoast(self, longitudeArray, latitudeArray):
        """ Function that takes a numpy 1D array of [lat, lon] and
        returns the distance to the coast"""
        
        # Generate the map indexes
        longIdx = np.zeros(longitudeArray.size)
        latIdx = np.zeros(latitudeArray.size)
        
        it = np.nditer([longitudeArray, latitudeArray, None, None])
        for longitude, latitude, longIdx, latIdx in it:
            longIdx[...] = np.argmin(np.abs(self.lons - longitude))
            latIdx[...] = np.argmin(np.abs(self.lats - latitude))
        
        #Lookup into map
        distanceArray = self.coastalData[it.operands[2].astype(int), it.operands[3].astype(int)]
        
        return distanceArray
    
    def displayMapTest(self):
        """ Test display the map over a grid of latitude-longitude points
        """
        
        #To run the test do:
        #coastalDistanceMap = CoastalDistanceMap()
        #coastalDistanceMap.loadMap(os.path.join(os.getcwd(), 'GNSSR_Python', 'landDistGrid_0.10LLRes_hGSHHSres.nc'))
        #coastalDistanceMap.DisplayMapTest()
        
        mapPlotter = MapPlotter(200e3) #Map grid in km (at equator)

        coastDistance = np.zeros((mapPlotter.sizeLat, mapPlotter.sizeLon))
        lons = np.zeros((mapPlotter.sizeLat, mapPlotter.sizeLon))
        lats = np.zeros((mapPlotter.sizeLat, mapPlotter.sizeLon))

        for indexes, x in np.ndenumerate(coastDistance):
            lon = np.array(mapPlotter.scaleLon[indexes[1]])
            lat = np.array(mapPlotter.scaleLat[indexes[0]])

            # Fill in output table
            coastDistance[indexes[0]][indexes[1]] = self.getDistanceToCoast(lon, lat)
            
        #Reshape to 2D map
        np.reshape(coastDistance, (mapPlotter.sizeLon, mapPlotter.sizeLat))
        #Plot
        mapPlotter.plotMapStatic(coastDistance)