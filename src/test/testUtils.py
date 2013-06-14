'''
Created on Oct 27, 2012

@author: john
'''
import unittest
from os.path import join, exists, abspath, dirname, pardir
from os import chdir
from shutil import rmtree
from dom import utils
from errorhandling.cursa_exceptions import CursaException
import config


class testUtils(unittest.TestCase):

    def setUp(self):
        config.cursa_home = abspath(join(dirname(__file__),
                                  pardir,
                                  pardir,
                                  'test_data'
                                  )
                            )

    def tearDown(self):
        if exists(config.cursa_home):
            rmtree(config.cursa_home)

    def test_make_dir_success(self):
        success_path = join(config.cursa_home, 'test_dir')
        utils.make_dir(success_path)
        self.assertTrue(exists(success_path))

    def test_make_dir_fail(self):
        # Failure - permission denied
        fail_path = '/test'
        with self.assertRaises(CursaException) as context:
            utils.make_dir(fail_path)

        expected_msg = 'Error creating directory at /test'
        self.assertEqual(context.exception.message, expected_msg)
        self.assertFalse(exists(fail_path))

    def test_make_dirs(self):
        paths = [join(config.cursa_home, 'test_dir1'),
                 join(config.cursa_home, 'test_dir2'),
                 join(config.cursa_home, 'test_dir3')]

        utils.make_dirs(paths)

        for path in paths:
            self.assertTrue(exists(path))

    def test_create_file_success(self):
        utils.make_dir(join(config.cursa_home, 'testFile'))
        utils.create_file(join(config.cursa_home, 'testFile', 'file.txt'))
        self.assertTrue(exists(join(config.cursa_home, 'testFile', 'file.txt')))

    def test_create_file_fail(self):
        testfile = join(config.cursa_home, 'testFile', 'file.txt')
        with self.assertRaises(CursaException) as context:
            utils.create_file(testfile)

        expected_msg = 'Error creating file at {0}'.format(testfile)
        self.assertEqual(context.exception.message, expected_msg)

        self.assertFalse(exists(join(config.cursa_home, 'testFile', 'file.txt')))

    def testCreateFiles(self):
        utils.make_dir(join(config.cursa_home, 'testFile'))

        testArray = [join(config.cursa_home, 'testFile', 'test1.txt'),
                     join(config.cursa_home, 'testFile', 'test2.txt'),
                     join(config.cursa_home, 'testFile', 'test3.txt')]

        utils.create_files(testArray)
        self.assertTrue(exists(join(config.cursa_home, 'testFile', 'test1.txt')))
        self.assertTrue(exists(join(config.cursa_home, 'testFile', 'test2.txt')))
        self.assertTrue(exists(join(config.cursa_home, 'testFile', 'test3.txt')))

    def test_create_yaml_template_success(self):
        utils.make_dir(join(config.cursa_home, 'testFile'))
        template = """type        : Course_section
title       : title
module      : test_module
topic       : test_topic
lab         : test_lab"""

        testdir = join(config.cursa_home, 'testFile')
        utils.create_yaml_template(testdir, template)
        self.assertTrue(exists(join(testdir, 'index.yaml')))

        with open(join(config.cursa_home, 'testFile', 'index.yaml')) as index:
            result = index.read()

        self.assertEquals(result, template)

    def test_create_yaml_template_fail(self):
        with self.assertRaises(CursaException) as context:
            utils.create_yaml_template('/test', 'test')
        expected_msg = 'Error creating YAML file at /test'
        self.assertEqual(context.exception.message, expected_msg)

    def test_delete_files_success(self):
        utils.make_dir(join(config.cursa_home, 'testFile'))
        filelist = [join(config.cursa_home, 'testFile', '1.html'),
                    join(config.cursa_home, 'testFile', '2.html'),
                    join(config.cursa_home, 'testFile', '3.html'),
                    join(config.cursa_home, 'testFile', '4.html')]

        utils.create_files(filelist)

        utils.delete_files(filelist, config.cursa_home)

        for each_file in filelist:
            self.assertFalse(exists(each_file))

        chdir(abspath(join(config.cursa_path, pardir)))

    def test_delete_files_fail(self):
        path = join(config.cursa_home, 'testFile')
        utils.make_dir(path)

        # File doesnt exist
        file_not_exist = join(config.cursa_home, 'testFile', '1.html')
        filelist = [file_not_exist]

        with self.assertRaises(CursaException) as context:
            utils.delete_files(filelist, config.cursa_home)

        expected_msg = 'Error deleting file {0} in {1}'.format(file_not_exist,
                                                               config.cursa_home)

        self.assertEqual(context.exception.message, expected_msg)

        # File is a path
        filelist = [join(config.cursa_home, 'testFile')]
        with self.assertRaises(CursaException) as context:
            utils.delete_files(filelist, config.cursa_home)

        expected_msg = 'Error deleting file {0} in {1}'.format(filelist[0],
                                                               config.cursa_home)

        self.assertEqual(context.exception.message, expected_msg)

        chdir(abspath(join(config.cursa_home, pardir)))

    def test_read_data_from_file_fail(self):
        # File doesnt exist
        with self.assertRaises(CursaException) as context:
            utils.read_data_from_file('/test/file.txt')

        expected_msg = 'Error opening file at /test/file.txt'
        self.assertEqual(context.exception.message, expected_msg)

    def test_copy_files_fail(self):
        # File doesnt exist
        with self.assertRaises(CursaException) as context:
            utils.copy_files(['/test/file.txt'], config.cursa_home)

        expected_msg = 'Error copying file {0} to {1}'.format('/test/file.txt',
                                                             config.cursa_home)

        self.assertEqual(context.exception.message, expected_msg)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
