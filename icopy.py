# -*- coding: UTF-8 -*-
import time
from os import path, walk, makedirs, error
import logging as log
import threading
import shutil
import filecmp
import sys

import exifread

VIDEO_FILE_DIR = "Videot"
IMAGE_FILE_DIR = "Kuvat"
OTHER_FILES_DIR = "muut_tiedostot"
OTHER_IMAGES_DIR = OTHER_FILES_DIR
DTO_KEY = "EXIF DateTimeOriginal"

class ImageCopy(threading.Thread):
    def __init__(self, source, target, test_without_copy=True):
        threading.Thread.__init__(self)
        self.copyfrom = path.normpath(source.replace("\ ", " "))
        self.copyto = path.normpath(target.replace("\ ", " "))
        self.move_manually_folder = OTHER_IMAGES_DIR
        self.otherfiles = OTHER_FILES_DIR
        self.test_without_copy = test_without_copy
        self.nmbr_files_copyed = 0
        self.nmbr_files_total = 0

    def run(self):
        self.copy_files()

    # @staticmethod
    # def _enctoutf8(source):
    #     if isinstance(source, str):
    #         return str(source, 'utf-8', 'ignore')
    #     else:
    #         return source

    def copy_files(self):
        """
        Searches defined files starting from 'searchroot'
        """
        picturefiles = ('.jpg', '.gif', '.bmp', '.tiff', '.tif')
        videofiles = ('.avi', '.mov', '.mp4', '.mv4', '.3gp', '.mpg')

        self.nmbr_files_copyed = 0
        self.nmbr_files_total = 0

        if self.copyfrom == self.copyto:
            log.warning("Source and target directories cannot be same!")
            return
        if not path.isdir(self.copyfrom):
            log.warning("Source is not directory!")
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
                    else:
                        log.info("File %s not copied.", source)

        log.info("Number files copyed: {0}".format(str(self.nmbr_files_copyed)))
        log.info("Total number of files: {0}".format(str(self.nmbr_files_total)))

    def _copy_one_file(self, source, filetype):
        log.info("Source file: " + source)
        if filetype != OTHER_FILES_DIR:
            target_dir = self.get_directoryname(source, filetype)
            target_dir = path.join(filetype, target_dir)
        else:
            target_dir = OTHER_FILES_DIR

        target_dir = self.create_directory(target_dir)
        errors = []
        if target_dir:
            count = 1
            target_file = path.join(target_dir, path.basename(source))
            while path.isfile(target_file):
                # if there is different file with same name add (x) to filename
                # e.g. kuva(2).jpg
                if filecmp.cmp(source, target_file, shallow=False):
                    log.info("File exists with name %s in the directory", target_file)
                    return
                if count == 1:
                    temp_arr = target_file.rsplit('.', 1)
                    target_file = temp_arr[0] + '(1).' + temp_arr[1]
                else:
                    temp_arr = target_file.rsplit('(', 1)
                    temp_arr[1] = '(' + str(count) + temp_arr[1][temp_arr[1].rindex(')'):]
                    target_file = temp_arr[0] + temp_arr[1]
                count += 1
            try:
                # copy file
                if not self.test_without_copy:
                    shutil.copy2(source, target_file)
                    log.info("Copied file: " + target_file)
                    self.nmbr_files_copyed += 1
                else:
                    self.nmbr_files_copyed += 1
                    log.info("Target file: " + target_file)

            except (IOError, error) as why:
                errors.append((source, target_file, str(why)))
                log.warning("Copying failed: " + target_file)

    def create_directory(self, trgt_dir):
        # create path with new directory name
        trgt_dir = path.join(self.copyto, trgt_dir)
        trgt_dir = path.normpath(trgt_dir)
        if not path.isdir(trgt_dir):
            try:
                if not self.test_without_copy:
                    makedirs(trgt_dir)
                log.info("Created directory: " + trgt_dir)
            except (error) as err:
                log.warning("Couldn't create directory: " + trgt_dir)
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
            log.info("File creation time missing for file %s! File moved to %s",source, self.move_manually_folder)
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
            # if ctime is None:
            #     ctime = self.get_creationtime(source)
        return ctime

    @staticmethod
    def get_exif_creationtime(source):
        f = open(source, 'rb')
        tags = exifread.process_file(f, details=False, stop_tag=DTO_KEY)
        f.close()
        if DTO_KEY in tags:
            ctime = str(tags[DTO_KEY])
            if "0000" == ctime[0:4]: #If year is zero then return None
                return None
            else:
                return ctime
        else:
            return None

    @staticmethod
    def get_creationtime(source):
        """ Return local time format:
                time.struct_time(tm_year=2013, tm_mon=5, tm_mday=22, tm_hour=17,
                tm_min=43, tm_sec=0, tm_wday=2, tm_yday=142, tm_isdst=1)
        """

            # On Windows use getctime()
            # ltime = time.localtime(path.getctime(source))

            # On POSIX system use getmtime()
            # At least Windows 10 seems to be POSIX

        ltime = time.localtime(path.getmtime(source))

        ctime = time.strftime("%Y:%m", ltime)
        log.debug("getmtime returned %s", ctime)
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
