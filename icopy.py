# -*- coding: cp1252 -*-
import time
import exifread
from os import path, walk, makedirs
from platform import system

class ImageCopy:
    key = "EXIF DateTimeOriginal"
    picturefiles = ('.tiff', '.jpg')
    videofiles = ('.avi', '.mov', '.mp4', '.mv4', '3gp')
    video_target_root = "Videos"
    months = {'01': 'Tammikuu', '02': 'Helmikuu', '03': 'Maaliskuu', '04': 'Huhtikuu',
              '05': 'Toukokuu', '06': 'Kesäkuu', '07': 'Heinäkuu', '08': 'Elokuu',
              '09': 'Syyskuu', '10': 'Lokakuu', '11': 'Marraskuu', '12': 'Joulukuu'}

    def __init__(self, source, target, copy=False):
        self.copyfrom = source
        self.copyto = target
        self.move_manually_folder = ImageCopy.create_directory(self, "move_manually")
        self.copy = copy
        #self.number_of_files = 0
        #self.number_

    def copy_files(self):
        """
        Searches defined files starting from 'searchroot'
        """

        for root, dirs, files in walk(self.copyfrom, topdown=True):
            for name in files:
                if name[name.rfind('.'):].lower() in self.picturefiles:
                    source = path.join(root, name)
                    print("Source file:" + source)
                    self.copy_imagefile(source)
                elif name[name.rfind('.'):].lower() in self.videofiles:
                    source = path.join(root, name)
                    print("Source file:" + source)
                    self.copy_videofile(source)

    def copy_imagefile(self, source):
        dir = self.get_directoryname(source)
        dir = path.join("Images", dir)
        dir = self.create_directory(dir)
        print("Image target directory: "+dir)

    def copy_videofile(self, source):
        dir = self.get_directoryname(source)
        dir = path.join("Videos", dir)
        dir = self.create_directory(dir)
        print("Video target directory: "+dir)

    def create_directory(self, dir):

        #create path with new directory name
        dir = path.join(self.copyto, dir)
        dir = path.normpath(dir)
        if not path.isdir(dir):
            try:
                makedirs(dir)
                print("Created directory:" + dir )
            except:
                print("Couldn't create directory: " + dir)
                dir = None
        return dir

    def get_directoryname(self, source):
        # localtime format in EXIF tag: 2012:06:23 14:26:30
        ctime = self.get_file_creationtime(source)

        if ctime is None:
            print("File creation time missing! File moved to "+ self.move_manually_folder)
            dirname = self.move_manually_folder
        else:
            dirname = ctime[:4] + "-" + ctime[5:7] + " " + self.months[ctime[5:7]]

        return dirname

    def get_file_creationtime(self, source):
        # localtime format in EXIF tag: 2012:06:23 14:26:30
        ctime = self.get_exif_creationtime(source)
        if ctime is None:
            """ Check file name for date i.e ddmmyyyyxxx.jpg. if it has a date use it"""
            ctime = self.get_filenamedate(source)
            if ctime is None:
                ctime = self.get_creationtime(source)
        return ctime

    def get_exif_creationtime(self, source):
        f = open(source, 'rb')
        tags = exifread.process_file(f, details=False, stop_tag=self.key)
        f.close()
        if self.key in tags:
            return str(tags[self.key])
        else:
            return None

    def get_creationtime(self, source):
        """ Return local time format:
                time.struct_time(tm_year=2013, tm_mon=5, tm_mday=22, tm_hour=17,
                tm_min=43, tm_sec=0, tm_wday=2, tm_yday=142, tm_isdst=1)
        """

        if system() is 'Windows':
            #On Windows use getctime()
            ltime = time.localtime(path.getctime(source))
        else:
            #On POSIX system use getmtime()
            ltime = time.localtime(path.getmtime(source))

        ctime = time.strftime("%Y:%m", ltime)
        return str(ctime)

    def get_filenamedate(self, source):
        filename = source.replace("\\", "/")
        filename = filename[filename.rfind("/") + 1:]

        # if file name has time format as ddmmyyyy
        if filename.isdigit() and \
                        int(filename[:2]) <= 31 and \
                                0 < int(filename[1:3]) <= 12 and \
                                1999 <= int(filename[3:7]) < 2030:
            return str(filename[3:7] + ":" + filename[:1])
        else:
            return None

test = ImageCopy("images", "copyed_images")
test.copy_files()