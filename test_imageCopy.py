# -*- coding: UTF-8 -*-

from unittest import TestCase
from os import getcwd, path, remove
from shutil import rmtree
from icopy import *


class ImageCopySetupTestCase(TestCase):
    def setUp(self):
        current_dir = getcwd()
        source = path.join(current_dir, "ätest_source")
        self.target = path.join(current_dir, "ööö_target")
        self.ic = ImageCopy(source, self.target, test_without_copy=False)
        self.assertIsNotNone(self.ic)

    def tearDown(self):
        del(self.ic)
        #self.ic = None
        rmtree(self.target)

    def test_copyfiles(self):
        self.ic.copy_files()
        self.assertEqual(self.ic.nmbr_files_copyed, 14)

    def test_copyfiles_two_times(self):
        self.ic.copy_files()
        self.assertEqual(self.ic.nmbr_files_copyed, 14)
        remove("ööö_target/Kuvat/2008-05 Toukokuu/18052008040.jpg")
        remove("ööö_target/muut_tiedostot/filet(1).txt")
        self.ic.copy_files()
        self.assertEqual(self.ic.nmbr_files_copyed, 2)

class TestImageCopyGetFileDate(TestCase):
    def test_get_exif_creationtime_None(self):
        file = 'ätest_source/Kuva027_no_exif.jpg'
        self.assertIsNone(ImageCopy.get_exif_creationtime(file))

    def test_get_exif_creationtime(self):
        file = 'ätest_source/Kuva 030.jpg'
        self.assertEqual(ImageCopy.get_exif_creationtime(file), '2004:12:24 18:44:56')

    def test_get_creationtime(self):
        file = 'ätest_source/Kuva027_no_exif.jpg'
        self.assertEqual(ImageCopy.get_creationtime(file), '2008:12')

    def test_get_filenamedate_None(self):
        file = 'ätest_source/Kuva 030.jpg'
        self.assertIsNone(ImageCopy.get_filenamedate(file))

    def test_get_filenamedate_yyyymmdd(self):
        file = 'ätest_source/20040319 Kuva 120.jpg'
        self.assertEqual(ImageCopy.get_filenamedate(file), '2004:03')

    def test_get_filenamedate_ddmmyyyy(self):
        file = 'ätest_source/18052008040.jpg'
        self.assertEqual(ImageCopy.get_filenamedate(file), '2008:05')

    def test_get_filenamedate_yyyymmdd_separatedbydash(self):
        file = 'ätest_source/2013-07-28 10.31.56.mp4'
        self.assertEqual(ImageCopy.get_filenamedate(file), '2013:07')

    def test_get_filenamedate_ddmmyyyy_with_dots(self):
        file = 'ätest_source/24.11.2008 075.jpg'
        self.assertEqual(ImageCopy.get_filenamedate(file), '2008:11')

