# -*- coding: UTF-8 -*-
import time
from os import path, walk, makedirs, error
from platform import system
import shutil
import filecmp
import sys

import exifread

VIDEO_FILE_DIR = "Videot"
IMAGE_FILE_DIR = "Kuvat"
OTHER_IMAGES_DIR = "muut_kuvat"
OTHER_FILES_DIR = "muut_tiedostot"
DTO_KEY = "EXIF DateTimeOriginal"


def log(text):
    sys.stdout.write(text + '\n')
    sys.stdout.flush()


class ImageCopy:
    def __init__(self, source, target, test_without_copy=True):

        self.copyfrom = path.normpath(source.replace("\ ", " "))
        self.copyto = path.normpath(target.replace("\ ", " "))
        self.move_manually_folder = OTHER_IMAGES_DIR
        self.otherfiles = OTHER_FILES_DIR
        self.test_without_copy = test_without_copy
        self.nmbr_files_copyed = 0
        self.nmbr_files_total = 0

    @staticmethod
    def _enctoutf8(source):
        if isinstance(source, str):
            return str(source, 'utf-8', 'ignore')
        else:
            return source

    def copy_files(self):
        """
        Searches defined files starting from 'searchroot'
        """
        picturefiles = ('.jpg', '.gif', '.bmp', '.tiff', '.tif')
        videofiles = ('.avi', '.mov', '.mp4', '.mv4', '.3gp', '.mpg')

        self.nmbr_files_copyed = 0
        self.nmbr_files_total = 0

        if self.copyfrom == self.copyto:
            print("Source and target directories cannot be same!")
            return
        if not path.isdir(self.copyfrom):
            print("Source is not directory!")
            return

        for root, dirs, files in walk(self.copyfrom, topdown=True):
            self.nmbr_files_total += len(files)
            for name in files:
                # get filename with path
                source = path.join(root, name)
                if name[name.rfind('.'):].lower() in picturefiles:
                    self._copy_one_file(source, IMAGE_FILE_DIR)
                elif name[name.rfind('.'):].lower() in videofiles:
                    self._copy_one_file(source, VIDEO_FILE_DIR)
                else:
                    # copy other files to OTHER_FILES_DIR.
                    # Ignore files and dirs starting with '.' and file names without file type information.
                    if not('.' in name[0:1] or '.' in root[0:1] or '.' not in name[1:]):
                        self._copy_one_file(source, OTHER_FILES_DIR)

        log("Number files copyed: {0}\nTotal number of files: {1}".format(str(self.nmbr_files_copyed),
                                                                             str(self.nmbr_files_total)))

    def _copy_one_file(self, source, filetype):
        log("Source file: " + source)
        if filetype != OTHER_FILES_DIR:
            trgt_dir = self.get_directoryname(source, filetype)
            trgt_dir = path.join(filetype, trgt_dir)
        else:
            trgt_dir = OTHER_FILES_DIR

        trgt_dir = self.create_directory(trgt_dir)
        errors = []
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
                    log("Copyed file: " + trgt_file)
                    shutil.copy2(source, trgt_file)
                    self.nmbr_files_copyed += 1
                else:
                    log("Target file: " + trgt_file)

            except (IOError, error) as why:
                errors.append((source, trgt_file, str(why)))
                log("Copying failed: " + trgt_file)

    def create_directory(self, trgt_dir):
        # create path with new directory name
        trgt_dir = path.join(self.copyto, trgt_dir)
        trgt_dir = path.normpath(trgt_dir)
        if not path.isdir(trgt_dir):
            try:
                makedirs(trgt_dir)
                log("Created directory:" + trgt_dir)
            except (error) as err:
                log("Couldn't create directory: " + trgt_dir)
                if trgt_dir.endswith(OTHER_FILES_DIR):
                    return None
                else:
                    return self.otherfiles
        return trgt_dir

    def get_directoryname(self, source, filetype):
        # localtime format in EXIF tag: 2012:06:23 14:26:30
        months = {'01': 'Tammikuu', '02': 'Helmikuu', '03': 'Maaliskuu', '04': 'Huhtikuu',
                  '05': 'Toukokuu', '06': 'Kesäkuu', '07': 'Heinäkuu', '08': 'Elokuu',
                  '09': 'Syyskuu', '10': 'Lokakuu', '11': 'Marraskuu', '12': 'Joulukuu'}

        ctime = self.get_file_creationtime(source, filetype)

        if ctime is None:
            log("File creation time missing! File moved to " + self.move_manually_folder)
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
            ctime = str(tags[DTO_KEY])
            if ctime[0:3] is "0000": #If year is zero then return None
                return None
            else:
                return None
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

        # replace characters in filename
        for c in ['-', '.', ':', ' ']:
            filename = filename.replace(c, "")

        # if file name has time format as ddmmyyyy
        if filename[:8].isdigit() and \
                        int(filename[:2]) <= 31 and \
                                0 < int(filename[2:4]) <= 12 and \
                                1999 <= int(filename[4:8]) < 2030:
            return str(filename[4:8] + ":" + filename[2:4])
        # if file name has time format as yyyymmdd
        elif filename[:8].isdigit() and \
                        int(filename[6:8]) <= 31 and \
                                0 < int(filename[4:6]) <= 12 and \
                                1999 <= int(filename[:4]) < 2030:
            return str(filename[0:4] + ":" + filename[4:6])

        else:
            return None
