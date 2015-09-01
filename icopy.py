# -*- coding: cp1252 -*-
import os
import time
import exifread

path = r"images/"
key = "EXIF DateTimeOriginal"
pictureFiles = ('.tiff', '.jpg')
videoFiles = ('.avi', '.mov', '.mp4', 'mv4')
pictureTargetRoot = r"C:\Users\nasiipet\Pictures"
videoTargetRoot = r"C:\Users\nasiipet\Videos"
targetFolderTemplate = "yyyy-mm "
months = {'01': 'Tammikuu', '02': 'Helmikuu', '03': 'Maaliskuu', '04': 'Huhtikuu',
          '05': 'Toukokuu', '06': 'Kesäkuu', '07': 'Heinäkuu', '08': 'Elokuu',
          '09': 'Syyskuu', '10': 'Lokakuu', '11': 'Marraskuu', '12': 'Joulukuu'}


def getFileNamesWithFullPath(searchRoot):
    """
    Searches defined files starting from 'searchroot'
    """
    
    for root, dirs, files in os.walk(path, topdown=True):
        for name in files:
            if name[name.rfind('.'):].lower() in pictureFiles:
                print("Copying "+os.path.join(root, name))
                source = os.path.join(root, name)
                copyImageFile(source)
            elif name[name.rfind('.'):].lower() in videoFiles:
                print("Copying "+os.path.join(root, name))
                source = os.path.join(root, name)
                copyVideoFile(source)
            

def copyImageFile(source):
    #localtime format in EXIF tag: 2012:06:23 14:26:30
    ctime = getFileCreationTime(source)    
    print("ctime: "+ctime)
    if ctime == None:
        print("File creation time missing!")
    else:
        dirName = ctime[:4]+"-"+ctime[5:7]+" "+months[ctime[5:7]]
    #os.path
    print("Directory name is: "+dirName)
    
def copyVideoFile(source):
    pass

def getFileCreationTime(source):
    #localtime format in EXIF tag: 2012:06:23 14:26:30
    ctime = getExifCreationTime(source)
    if ctime == None:
        """ Check file name for date i.e ddmmyyyyxxx.jpg. if it has a date use it"""
        ctime = checkFileNameForDate(source)
        if ctime == None:
            ctime = getCreationTime(source)
    return ctime

def getExifCreationTime(source):    
    f = open(source, 'rb')        
    tags = exifread.process_file(f, details=False)
    f.close()
    if key in tags:
        return str(tags["EXIF DateTimeOriginal"])        
    else:        
        return None

def getCreationTime(source):
    """ Return local time format:
            time.struct_time(tm_year=2013, tm_mon=5, tm_mday=22, tm_hour=17,
            tm_min=43, tm_sec=0, tm_wday=2, tm_yday=142, tm_isdst=1)
    """
    ltime = time.localtime(os.path.getctime(source))
    ctime = time.strftime("%Y:%m", ltime)
    print("File timestamp"+ctime)
    return str(ctime)
               
def checkFileNameForDate(source):
    print "Source: "+source
    fileName = source.replace("\\","/")    
    fileName = fileName[fileName.rfind("/")+1:]
    print "Filename: "+fileName  
    # if file name has time format as ddmmyyyy
    if fileName.isdigit() and \
        int(fileName[:2]) > 0 and int(fileName[:2]) <= 31 and \
        int(fileName[1:3]) > 0 and int(fileName[1:3]) <= 12 and \
        int(fileName[3:7]) >= 1999 and int(fileName[3:7]) < 2020:
        
        return str(filename[3:7]+":"+filename[:1])
    else:
        return None
        
getFileNamesWithFullPath(path)



