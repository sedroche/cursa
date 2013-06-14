'''
Created on Oct 27, 2012

@author: john
'''
import unittest
from os.path import join, exists, abspath, dirname, pardir
from os import remove
from shutil import rmtree, make_archive
from dom.webserviceclient import WebServiceClient
import requests
from tempfile import mkdtemp
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

    def test_send_file_resource_success(self):
        # Monkey patch the requests.post function
        requests.post = _dummy_requests_post

        params = {
                     'courseid': '7',
                     'sectionid': '3',
                     'type': 'file',
                     'displayname': 'test display name',
                     'mainfile': '',
                     'mainfilepath': '',
                     'labeltext': '',
                     'labeltextformat': ''
                  }

        tmpdir = mkdtemp()
        file_to_send = make_archive(tmpdir, 'zip', root_dir=tmpdir)

        json_resonse = WebServiceClient().send_resource(params, file_to_send)

        expected_response = {
                                'courseid': '7',
                                'sectionid': '3',
                                'cmid': '123'
                             }

        self.assertEquals(json_resonse, expected_response)
        remove(file_to_send)
        rmtree(tmpdir)

    def test_send_label_resource_success(self):
        # Monkey patch the requests.post function
        requests.post = _dummy_requests_post

        params = {
                     'courseid': '8',
                     'sectionid': '4',
                     'type': 'label',
                     'displayname': '',
                     'mainfile': 'file.html',
                     'mainfilepath': '/html/',
                     'labeltext': '##this is markdown',
                     'labeltextformat': 'markdown'
                  }

        json_resonse = WebServiceClient().send_resource(params)

        expected_response = {
                                'courseid': '8',
                                'sectionid': '4',
                                'cmid': '123'
                             }

        self.assertEquals(json_resonse, expected_response)

    def test_send_file_resource_fail_connection(self):
        params = {
                     'courseid': '7',
                     'sectionid': '3',
                     'type': 'file',
                     'displayname': 'test display name',
                     'mainfile': '',
                     'mainfilepath': '',
                     'labeltext': '',
                     'labeltextformat': ''
                  }

        tmpdir = mkdtemp()
        file_to_send = make_archive(tmpdir, 'zip', root_dir=tmpdir)

        with self.assertRaises(CursaException) as context:
            WebServiceClient().send_resource(params, file_to_send)

        expected_msg = 'Connection failed'
        self.assertEqual(context.exception.message, expected_msg)

        remove(file_to_send)
        rmtree(tmpdir)

    def test_send_file_resource_fail_I0(self):
        params = {
                     'courseid': '7',
                     'sectionid': '3',
                     'type': 'file',
                     'displayname': 'test display name',
                     'mainfile': '',
                     'mainfilepath': '',
                     'labeltext': '',
                     'labeltextformat': ''
                  }

        file_to_send = 'file/that/doesnt/exist.zip'

        with self.assertRaises(CursaException) as context:
            WebServiceClient().send_resource(params, file_to_send)

        expected_msg = 'Error opening file at file/that/doesnt/exist.zip'
        self.assertEqual(context.exception.message, expected_msg)


def _dummy_requests_post(url, data=None, **kwargs):
    return DummyResponse(**kwargs)


class DummyResponse(object):

    def __init__(self, **kwargs):
        self.jsonresponse = {
                                'courseid': kwargs['params']['courseid'],
                                'sectionid': kwargs['params']['sectionid'],
                                'cmid': '123'
                             }

    def raise_for_status(self):
        pass

    def json(self):
        return self.jsonresponse

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
