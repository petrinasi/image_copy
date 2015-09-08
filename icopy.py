# -*- coding: UTF-8 -*-
import time
from os import path, walk, makedirs
from platform import system
import shutil
import filecmp

import exifread

VIDEO_FILE_DIR = "Videot"
IMAGE_FILE_DIR = "Kuvat"
OTHER_IMAGES_DIR = "muut_kuvat"
OTHER_FILES_DIR = "muut_tiedostot"
DTO_KEY = "EXIF DateTimeOriginal"


class ImageCopy:
    def __init__(self, source, target, test_without_copy=True):
        self.copyfrom = path.normpath(source.replace("\ ", " "))
        self.copyto = path.normpath(target.replace("\ ", " "))
        self.move_manually_folder = ImageCopy.create_directory(self, OTHER_IMAGES_DIR)
        self.otherfiles = ImageCopy.create_directory(self, OTHER_FILES_DIR)
        self.test_without_copy = test_without_copy
        self.nmbr_files_copyed = 0
        self.nmbr_files_total = 0

    def copy_files(self):
        """
        Searches defined files starting from 'searchroot'
        """
        picturefiles = ('.tiff', '.jpg', '.gif', '.bmp')
        videofiles = ('.avi', '.mov', '.mp4', '.mv4', '3gp', '.mpg')

        if self.copyfrom == self.copyto:
            print("Source and target directories cannot be same!")
            exit()
        if not path.isdir(self.copyfrom):
            print("Source is not directory!")
            exit()

        for root, dirs, files in walk(self.copyfrom, topdown=True):
            self.nmbr_files_total += len(files)
            for name in files:
                if name[name.rfind('.'):].lower() in picturefiles:
                    source = path.join(root, name)
                    self.copy_one_file(source, IMAGE_FILE_DIR)
                elif name[name.rfind('.'):].lower() in videofiles:
                    source = path.join(root, name)
                    self.copy_one_file(source, VIDEO_FILE_DIR)
                else:
                    source = path.join(root, name)
                    if name[0] != '.':
                        self.copy_one_file(source, OTHER_FILES_DIR)

        print("Number files copyed: {0}\nTotal number of files: {1}".format(str(self.nmbr_files_copyed),
                                                                            str(self.nmbr_files_total)))

    def copy_one_file(self, source, filetype):
        print("Source file:" + source)
        if filetype != OTHER_FILES_DIR:
            trgt_dir = self.get_directoryname(source, filetype)
            trgt_dir = path.join(filetype, trgt_dir)
        else:
            trgt_dir = OTHER_FILES_DIR

        trgt_dir = self.create_directory(trgt_dir)

        if trgt_dir:
            count = 1
            trgt_file = path.join(trgt_dir, path.basename(source))
            while path.isfile(trgt_file):
                if filecmp.cmp(source, trgt_file, shallow=False):
                    return
                if count == 1:
                    temp_arr = trgt_file.rsplit('.', 1)
                    trgt_file = temp_arr[0] + '(1).' + temp_arr[1]
                else:
                    temp_arr = trgt_file.rsplit(')', 1)
                    trgt_file = temp_arr[0] + str(count) + ')' + temp_arr[1]
                count += 1
            try:
                if not self.test_without_copy:
                    shutil.copy2(source, trgt_file)
                self.nmbr_files_copyed += 1
                print("Target file : " + trgt_file)
            except:
                print("Copying failed: " + trgt_file)

    def create_directory(self, trgt_dir):
        # create path with new directory name
        trgt_dir = path.join(self.copyto, trgt_dir)
        trgt_dir = path.normpath(trgt_dir)
        if not path.isdir(trgt_dir):
            try:
                makedirs(trgt_dir)
                print("Created directory:" + trgt_dir)
            except:
                print("Couldn't create directory: " + trgt_dir)
                if trgt_dir.endswith(OTHER_FILES_DIR):
                    return None
                else:
                    return self.otherfiles
        return trgt_dir

    def get_directoryname(self, source, filetype):
        # localtime format in EXIF tag: 2012:06:23 14:26:30
        months = {'01': u'Tammikuu', '02': u'Helmikuu', '03': u'Maaliskuu', '04': u'Huhtikuu',
                  '05': u'Toukokuu', '06': u'Kesäkuu', '07': u'Heinäkuu', '08': u'Elokuu',
                  '09': u'Syyskuu', '10': u'Lokakuu', '11': u'Marraskuu', '12': u'Joulukuu'}

        ctime = self.get_file_creationtime(source, filetype)

        if ctime is None:
            print("File creation time missing! File moved to " + self.move_manually_folder)
            dirname = self.move_manually_folder
        else:
            dirname = ctime[:4] + "-" + ctime[5:7] + " " + months[ctime[5:7]]

        return dirname

    def get_file_creationtime(self, source, filetype):
        # localtime format in EXIF tag: 2012:06:23 14:26:30
        if filetype == IMAGE_FILE_DIR:
            ctime = self.get_exif_creationtime(source)
        else:
            ctime = None

        if ctime is None:
            """ Check file name for date i.e ddmmyyyyxxx.jpg. if it has a date use it"""
            ctime = self.get_filenamedate(source)
            if ctime is None:
                ctime = self.get_creationtime(source)
        return ctime

    @staticmethod
    def get_exif_creationtime(source):
        f = open(source, 'rb')
        tags = exifread.process_file(f, details=False, stop_tag=DTO_KEY)
        f.close()
        if DTO_KEY in tags:
            return str(tags[DTO_KEY])
        else:
            return None

    @staticmethod
    def get_creationtime(source):
        """ Return local time format:
                time.struct_time(tm_year=2013, tm_mon=5, tm_mday=22, tm_hour=17,
                tm_min=43, tm_sec=0, tm_wday=2, tm_yday=142, tm_isdst=1)
        """

        if system() is 'Windows':
            # On Windows use getctime()
            ltime = time.localtime(path.getctime(source))
        else:
            # On POSIX system use getmtime()
            ltime = time.localtime(path.getmtime(source))

        ctime = time.strftime("%Y:%m", ltime)
        return str(ctime)

    @staticmethod
    def get_filenamedate(source):
        filename = source.replace("\\", "/")
        filename = filename[filename.rfind("/") + 1:]
        filename.strip('-: ')
        # if file name has time format as ddmmyyyy
        if filename[:8].isdigit() and \
                        int(filename[:2]) <= 31 and \
                                0 < int(filename[2:4]) <= 12 and \
                                1999 <= int(filename[4:8]) < 2030:
            return str(filename[4:8] + ":" + filename[2:4])
        else:
            return None
