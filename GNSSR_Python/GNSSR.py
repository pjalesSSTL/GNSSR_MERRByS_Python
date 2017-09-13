'''Set of functions for processing GNSS-R data from www.MERRByS.co.uk'''


def FindFiles(startTime, stopTime):
    '''Returns a list of all file names that would be present between the startTime and stopTime
          File names would be in format yyyy-mm/dd/Hhh which are segmented into 6 hour segments'''
    
    import datetime
    
    thisStartTime = startTime
    processStopTime = stopTime

    segmentationTimeHours = datetime.timedelta(hours=6)
    
    thisStopTime = thisStartTime + segmentationTimeHours
    # Loop through all time segments from processStartTime
    timeRangeList = [];
    while thisStopTime <= processStopTime:
        # Add to list for processing
        timeRangeList.append((thisStartTime, thisStopTime))

        # Move to the next step
        thisStartTime = thisStartTime + segmentationTimeHours
        thisStopTime = thisStartTime + segmentationTimeHours
        
    return timeRangeList

def FolderFromTimeStamp(timeRange):
    '''Get the folder that the data will be stored in from the time range '''
    import datetime
    
    monthlyFolderName = str(timeRange[0].year).zfill(4) + "-" + str(timeRange[0].month).zfill(2)
    if timeRange[1] - timeRange[0] < datetime.timedelta(hours=23, minutes=59, seconds=58):
        midPointTime = (timeRange[1] - timeRange[0]) / 2 + timeRange[0]
        dailyFolderName = str(midPointTime.day).zfill(2) + "/H" + str(midPointTime.hour).zfill(2)
    else:
        dailyFolderName = str(timeRange[0].day).zfill(2)

    return monthlyFolderName + "/" + dailyFolderName

def MatlabToPythonDateNum(matlab_datenum):
    '''Convert Matlab datenum to python datetime'''
    import datetime
    
    day = datetime.datetime.fromordinal(int(matlab_datenum))
    dayfrac = datetime.timedelta(days=matlab_datenum%1) - datetime.timedelta(days = 366)
    return day + dayfrac

def DownloadData(startTime, endTime, destination, ftpServer, userName, passWord, dataLevels):
    '''Download data from MERRByS server over the time-range
    Provided the following parameters:
        startTime, endTime: The time range to download
        destination:        The folder where the data should be stored
        ftpServer:          The string: 'ftp.merrbys.co.uk'
        userName, passWord: The credentials given to you on registration
        dataLevels:         The data levels to download {'L1B': True, 'L2_FDI': True}
        '''
    
    from ftplib import FTP, error_perm
    import os
    import sys
    import datetime
    
    #Ensure destination folder exists
    if not os.path.exists(destination):
        os.makedirs(destination)
         
    #List of files to collect from server
    #'L2_FDI.nc' is only in L2 data, and the rest only in L1. Script could be optimised to remove these checks
    fileList = []
    if dataLevels['L1B'] == True:
        fileList.append('metadata.nc')
        fileList.append('ddms.nc')
        fileList.append('directSignalPower.nc')
        fileList.append('blackbodyNadir.nc')
        fileList.append('blackbodyZenith.nc')
    if dataLevels['L2_FDI'] == True:
        fileList.append('L2_FDI.nc')

    ftp = FTP(ftpServer)
    ftp.login(user=userName, passwd = passWord) 

    #Generate a list of possible files
    dataList = FindFiles(startTime, endTime)
    
    print ('Starting download')
    itemsDownloaded = 0
    
    from ipywidgets import FloatProgress
    from IPython.display import display
    f = FloatProgress(min=1, max=len(dataList))
    display(f)
    
    #Main loop
    for entry in dataList:
        entryFolder = FolderFromTimeStamp(entry)
        for dataLevel in dataLevels:
            try:
                ftp.cwd('/Data/' + dataLevel + '/' + entryFolder)
            except Exception as e:
                # Continue on error as data may not be found
                continue      

            itemsDownloaded = itemsDownloaded + 1
            f.value += 1
            
            #print(entryFolder)
            
            for fileName in fileList:
                #Check that the file exists before opening it, as this creates empty files otherwise          
                try:
                    fileSize = ftp.size(fileName)
                except error_perm as e:
                    #Send e to an error file as needed
                    continue
                
                #Split the data and recombine as a valid path to the destination folder 
                ymd = entryFolder.split('/')
                fullPath = os.path.join(destination, dataLevel, ymd[0], ymd[1], ymd[2]) 
                
                #Create folders as needed
                if not os.path.exists(fullPath):
                    os.makedirs(fullPath)
                    
                #Create full path
                filePath = os.path.join(fullPath, fileName)
                
                if os.path.isfile(filePath):
                    #If the file exists, do not redownload
                    continue
                else:
                    ftp.retrbinary("RETR " + fileName, open(filePath, 'wb').write)

    print ('Complete. Got: ' + str(itemsDownloaded) + ' segments')
    f.value = len(dataList)
