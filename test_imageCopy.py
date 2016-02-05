# -*- coding: UTF-8 -*-

from unittest import TestCase
from os import getcwd, path, remove
from shutil import rmtree
import icopy


class ImageCopySetupTestCase(TestCase):
    def setUp(self):
        current_dir = getcwd()
        source = path.join(current_dir, "test_source")
        self.target = path.join(current_dir, "ööö_target")
        self.ic = icopy.ImageCopy(source, self.target, test_without_copy=False)
        self.assertIsNotNone(self.ic)

    def tearDown(self):
        del(self.ic)
        #self.ic = None
        rmtree(self.target)

    def test_copyfiles_two_times(self):
        self.ic.copy_files()
        self.assertEqual(self.ic.nmbr_files_copyed, 14)
        remove("ööö_target/Kuvat/2008-05 Toukokuu/18052008040.jpg")
        remove("ööö_target/muut_tiedostot/filet(1).txt")
        self.ic.copy_files()
        self.assertEqual(self.ic.nmbr_files_copyed, 2)

class TestImageCopyGetFileDate(TestCase):
    def test_get_exif_creationtime_None(self):
        file = 'test_source/Kuva027_no_exif.jpg'
        self.assertIsNone(icopy.ImageCopy.get_exif_creationtime(file))

    def test_get_exif_creationtime(self):
        file = 'test_source/Kuva 030.jpg'
        self.assertEqual(icopy.ImageCopy.get_exif_creationtime(file), '2004:12:24 18:44:56')

    def test_get_filenamedate_None(self):
        file = 'test_source/Kuva 030.jpg'
        self.assertIsNone(icopy.ImageCopy.get_filenamedate(file))

    def test_get_filenamedate_yyyymmdd(self):
        file = 'test_source/20040319 Kuva 120.jpg'
        self.assertEqual(icopy.ImageCopy.get_filenamedate(file), '2004:03')

    def test_get_filenamedate_ddmmyyyy(self):
        file = 'test_source/18052008040.jpg'
        self.assertEqual(icopy.ImageCopy.get_filenamedate(file), '2008:05')

    def test_get_filenamedate_yyyymmdd_separatedbydash(self):
        file = 'test_source/2013-07-28 10.31.56.mp4'
        self.assertEqual(icopy.ImageCopy.get_filenamedate(file), '2013:07')

    def test_get_filenamedate_ddmmyyyy_with_dots(self):
        file = 'test_source/24.11.2008 075.jpg'
        self.assertEqual(icopy.ImageCopy.get_filenamedate(file), '2008:11')

